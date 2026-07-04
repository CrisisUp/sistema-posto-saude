from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.database import DatabaseConnection

class PacienteCadastro(BaseModel):
    nome_paciente: str
    documento_unico: str
    nome_mae: str
    data_nascimento: str  
    gravidade: int        
    especialidade_id: int 

class AtendimentoRepository:
    """Responsável estritamente pela persistência e comunicação com o banco de dados."""
    def __init__(self):
        self.db = DatabaseConnection

    def inserir_na_fila(self, paciente: PacienteCadastro) -> None:
        with self.db.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO atendimentos (nome_paciente, documento_unico, nome_mae, data_nascimento, gravidade, status, especialidade_id)
                VALUES (?, ?, ?, ?, ?, 'AGUARDANDO', ?)
            """, (paciente.nome_paciente, paciente.documento_unico, paciente.nome_mae, paciente.data_nascimento, paciente.gravidade, paciente.especialidade_id))
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
            return dict(resultado) if resultado else None

    def atualizar_status_e_obter_nome(self, atendimento_id: int) -> Optional[str]:
        with self.db.obter_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE atendimentos SET status = 'CHAMADO', chamado_em = CURRENT_TIMESTAMP WHERE id = ?", (atendimento_id,))
            cursor.execute("SELECT nome_paciente FROM atendimentos WHERE id = ?", (atendimento_id,))
            resultado = cursor.fetchone()
            conn.commit()
            return resultado["nome_paciente"] if resultado else None

    def executar_transicao_de_status(self, atendimento_id: int, acao: str) -> None:
        with self.db.obter_conexao() as conn:
            cursor = conn.cursor()
            if acao == "INICIAR":
                cursor.execute("UPDATE atendimentos SET status = 'EM_ATENDIMENTO' WHERE id = ?", (atendimento_id,))
            elif acao == "FINALIZAR":
                cursor.execute("UPDATE atendimentos SET status = 'FINALIZADO' WHERE id = ?", (atendimento_id,))
            elif acao == "AUSENTE":
                cursor.execute("""
                    UPDATE atendimentos 
                    SET status = 'AGUARDANDO', criado_em = CURRENT_TIMESTAMP, chamado_em = NULL 
                    WHERE id = ?
                """, (atendimento_id,))
            conn.commit()