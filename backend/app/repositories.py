from typing import List, Optional, Dict, Any
from pydantic import BaseModel, field_validator, model_validator
from app.database import DatabaseConnection
from app.config import CHAVE_CRIPTOGRAFIA
from cryptography.fernet import Fernet
import re

# Inicializa o motor de criptografia com a nossa chave secreta
fernet = Fernet(CHAVE_CRIPTOGRAFIA)

# ==============================================================================
# CAMADA DE VALIDAÇÃO ESTREITA E HIGIENIZAÇÃO (DTO)
# ==============================================================================
class PacienteCadastro(BaseModel):
    nome_paciente: str
    tipo_documento: str   # <-- Campo Explícito: 'CPF' ou 'SUS'
    documento_unico: str
    nome_mae: str
    data_nascimento: str  
    gravidade: int        
    especialidade_id: int 

    @field_validator('tipo_documento')
    @classmethod
    def validar_tipo(cls, valor: str) -> str:
        tipo = valor.upper().strip()
        if tipo not in ["CPF", "SUS"]:
            raise ValueError("O tipo de documento deve ser explicitamente 'CPF' ou 'SUS'.")
        return tipo

    @field_validator('nome_paciente', 'nome_mae')
    @classmethod
    def evitar_caracteres_maliciosos(cls, valor: str) -> str:
        nome_limpo = re.sub(r'<[^>]*>', '', valor).strip()
        if not nome_limpo:
            raise ValueError("O nome inserido é inválido.")
        return nome_limpo

    @model_validator(mode='after')
    def validar_documento_por_tipo(self) -> 'PacienteCadastro':
        tipo = self.tipo_documento
        doc_limpo = re.sub(r'\D', '', self.documento_unico)
        
        if tipo == "CPF" and len(doc_limpo) != 11:
            raise ValueError("Para o tipo CPF, o documento deve conter exatamente 11 dígitos numéricos.")
        
        if tipo == "SUS" and len(doc_limpo) != 15:
            raise ValueError("Para o tipo SUS, o documento deve conter exatamente 15 dígitos numéricos.")
            
        self.documento_unico = doc_limpo
        return self


# ==============================================================================
# CAMADA DE REPOSITÓRIO COM CRIPTOGRAFIA E TIPO DE DOCUMENTO
# ==============================================================================
class AtendimentoRepository:
    def __init__(self):
        self.db = DatabaseConnection

    def inserir_na_fila(self, paciente: PacienteCadastro) -> None:
        documento_bytes = paciente.documento_unico.encode('utf-8')
        documento_cifrado = fernet.encrypt(documento_bytes).decode('utf-8')

        with self.db.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO atendimentos (nome_paciente, tipo_documento, documento_unico, nome_mae, data_nascimento, gravidade, status, especialidade_id)
                VALUES (?, ?, ?, ?, ?, ?, 'AGUARDANDO', ?)
            """, (paciente.nome_paciente, paciente.tipo_documento, documento_cifrado, paciente.nome_mae, paciente.data_nascimento, paciente.gravidade, paciente.especialidade_id))
            conn.commit()

    def buscar_proximo_da_fila(self, especialidade_id: int) -> Optional[Dict[str, Any]]:
        with self.db.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *, 
                       (strftime('%Y', 'now') - strftime('%Y', data_nascimento) >= 60) AS eh_idoso
                FROM atendimentos
                WHERE status = 'AGUARDANDO' AND especialidade_id = ?
                ORDER BY gravidade DESC, eh_idoso DESC, criado_em ASC
                LIMIT 1
            """, (especialidade_id,))
            resultado = cursor.fetchone()
            
            if not resultado:
                return None
                
            dados = dict(resultado)
            
            try:
                doc_descifrado = fernet.decrypt(dados["documento_unico"].encode('utf-8')).decode('utf-8')
                
                if dados["tipo_documento"] == "CPF":
                    dados["documento_unico"] = f"{doc_descifrado[:3]}.***.***-{doc_descifrado[-2:]}"
                elif dados["tipo_documento"] == "SUS":
                    dados["documento_unico"] = f"{doc_descifrado[:3]}.****.****.{doc_descifrado[-4:]} (SUS)"
                else:
                    dados["documento_unico"] = f"{doc_descifrado[:3]}************"
            except Exception:
                dados["documento_unico"] = "Erro ao decifrar dado"

            return dados

    def atualizar_status_e_obter_nome(self, atendimento_id: int, sala: str) -> Optional[str]:
        with self.db.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE atendimentos 
                SET status = 'CHAMADO', chamado_em = CURRENT_TIMESTAMP, sala_atendimento = ? 
                WHERE id = ?
            """, (sala, atendimento_id))
            
            cursor.execute("SELECT nome_paciente FROM atendimentos WHERE id = ?", (atendimento_id,))
            resultado = cursor.fetchone()
            conn.commit()
            return resultado["nome_paciente"] if resultado else None

    def executar_transicao_de_status(self, atendimento_id: int, acao: str) -> None:
        with self.db.obter_conexao() as conn:
            cursor = conn.cursor()
            if acao == "INICIAR":
                cursor.execute("UPDATE atendimentos SET status = 'EM_ATENDIMENTO' WHERE id = ?", (atendimento_id,))
            elif acao == "FINALIZADO":  # 🚨 AJUSTADO: Garante compatibilidade total com o log
                cursor.execute("UPDATE atendimentos SET status = 'FINALIZADO' WHERE id = ?", (atendimento_id,))
            elif acao == "AUSENTE":
                cursor.execute("""
                    UPDATE atendimentos 
                    SET status = 'AGUARDANDO', criado_em = CURRENT_TIMESTAMP, chamado_em = NULL 
                    WHERE id = ?
                """, (atendimento_id,))
            conn.commit()

    def obter_ultimo_chamado(self) -> Optional[Dict[str, Any]]:
        with self.db.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM atendimentos 
                WHERE status = 'CHAMADO'
                ORDER BY chamado_em DESC
                LIMIT 1
            """)
            resultado = cursor.fetchone()
            
            if not resultado:
                return None
                
            dados = dict(resultado)
            
            try:
                dados["documento_unico"] = fernet.decrypt(dados["documento_unico"].encode('utf-8')).decode('utf-8')
            except Exception:
                dados["documento_unico"] = "Erro"
                
            return dados
            
    # 🚨 CORREÇÃO: Método devidamente indentado e utilizando o motor Fernet correto
    def buscar_fila_por_especialidade(self, fireplace_id: int) -> List[Dict[str, Any]]:
        """Busca no banco SQLite os pacientes aguardando atendimento."""
        with self.db.obter_conexao() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT id, nome_paciente, tipo_documento, documento_unico, gravidade 
                FROM atendimentos 
                WHERE especialidade_id = ? AND status = 'AGUARDANDO'
                ORDER BY gravidade DESC, id ASC
                """,
                (fireplace_id,)
            )
            
            colunas = [col[0] for col in cursor.description]
            resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
            
            # Descriptografa os documentos em trânsito antes de mandar ao frontend
            for paciente in resultados:
                try:
                    doc_descifrado = fernet.decrypt(paciente["documento_unico"].encode('utf-8')).decode('utf-8')
                    if paciente["tipo_documento"] == "CPF":
                        paciente["documento_unico"] = f"{doc_descifrado[:3]}.***.***-{doc_descifrado[-2:]}"
                    elif paciente["tipo_documento"] == "SUS":
                        paciente["documento_unico"] = f"{doc_descifrado[:3]}.****.****.{doc_descifrado[-4:]}"
                    else:
                        paciente["documento_unico"] = f"{doc_descifrado[:3]}***"
                except Exception:
                    paciente["documento_unico"] = "Dado protegido"
                        
            return resultados