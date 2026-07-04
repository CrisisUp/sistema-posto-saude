from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from typing import List, Optional, Dict, Any
import sqlite3

app = FastAPI(title="Sistema do Posto de Saúde - Clean Code Edition")

# --- CONFIGURAÇÃO DE SEGURANÇA (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "../banco/posto_saude.db"


# ==============================================================================
# 1. CAMADA DE INFRAESTRUTURA / CONEXÃO (Database Factory)
# ==============================================================================
class DatabaseConnection:
    """Gerenciador central de conexões com o banco de dados SQLite."""
    @staticmethod
    def obter_conexao() -> sqlite3.Connection:
        conexao = sqlite3.connect(DB_PATH)
        conexao.row_factory = sqlite3.Row
        return conexao


# ==============================================================================
# 2. CAMADA DE MODELOS DE VALIDAÇÃO (DTOs / Pydantic)
# ==============================================================================
class PacienteCadastro(BaseModel):
    nome_paciente: str
    documento_unico: str
    nome_mae: str
    data_nascimento: str  
    gravidade: int        
    especialidade_id: int 


# ==============================================================================
# 3. CAMADA DE REPOSITÓRIO (Apenas consultas e comandos SQL)
# ==============================================================================
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


# ==============================================================================
# 4. CAMADA DE SERVIÇOS DE REDE (WebSockets)
# ==============================================================================
class GerenciadorTV:
    """Gerencia o canal de comunicação em tempo real com as TVs da sala de espera."""
    def __init__(self):
        self.conexoes_ativas: List[WebSocket] = []

    async def conectar(self, websocket: WebSocket):
        await websocket.accept()
        self.conexoes_ativas.append(websocket)

    def desconectar(self, websocket: WebSocket):
        if websocket in self.conexoes_ativas:
            self.conexoes_ativas.remove(websocket)

    async def enviar_chamada_tv(self, nome_paciente: str, sala: str):
        if not self.conexoes_ativas:
            return

        payload = {"nome": nome_paciente, "sala": sala}
        for conexao in list(self.conexoes_ativas):
            try:
                await conexao.send_json(payload)
            except Exception:
                self.desconectar(conexao)


# Inicialização dos serviços globais
repository = AtendimentoRepository()
gerenciador_tv = GerenciadorTV()


# ==============================================================================
# 5. CAMADA DE ROTAS / INTERFACE (Apenas controle de requisições HTTP e WS)
# ==============================================================================
@app.get("/")
def rota_inicial():
    return {"status": "Servidor do Posto de Saúde está online!"}


@app.post("/recepcao/cadastrar")
def cadastrar_paciente(paciente: PacienteCadastro):
    try:
        repository.inserir_na_fila(paciente)
        return {"status": "sucesso", "mensagem": f"Paciente {paciente.nome_paciente} inserido na fila!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao cadastrar: {str(e)}")


@app.get("/medico/proximo/{especialidade_id}")
def buscar_proximo_paciente(especialidade_id: int):
    try:
        paciente = repository.buscar_proximo_da_fila(especialidade_id)
        if not paciente:
            return {"mensagem": "Nenhum paciente aguardando nesta fila."}
        return paciente
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar próximo: {str(e)}")


@app.post("/medico/chamar/{atendimento_id}")
async def chamar_paciente(atendimento_id: int, sala: Optional[str] = None):
    try:
        nome_paciente = repository.get_nome_e_atualizar_chamada(atendimento_id) if hasattr(repository, 'get_nome_e_atualizar_chamada') else repository.atualizar_status_e_obter_nome(atendimento_id)
        
        if not nome_paciente:
            return {"status": "erro", "mensagem": "Atendimento não encontrado."}
            
        sala_final = sala if sala and "Consultório" in sala else f"Consultório {sala or '1'}"

        try:
            await gerenciador_tv.enviar_chamada_tv(nome_paciente, sala_final)
        except Exception:
            pass

        return {"status": "sucesso", "mensagem": "Paciente chamado no painel!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao disparar chamada: {str(e)}")


@app.post("/medico/status/{atendimento_id}")
def alterar_status_atendimento(atendimento_id: int, acao: str):
    try:
        repository.executar_transicao_de_status(atendimento_id, acao)
        return {"status": "sucesso", "mensagem": f"Ação {acao} processada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao alterar status: {str(e)}")


# --- CANAIS E ARQUIVOS ESTÁTICOS ---
@app.websocket("/ws/tv")
async def websocket_tv_endpoint(websocket: WebSocket):
    await gerenciador_tv.conectar(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        gerenciador_tv.desconectar(websocket)


@app.get("/tela-medico", response_class=HTMLResponse)
def abrir_tela_medico():
    with open("medico.html", "r", encoding="utf-8") as arquivo:
        return arquivo.read()


@app.get("/tela-tv", response_class=HTMLResponse)
def abrir_tela_tv():
    with open("tv.html", "r", encoding="utf-8") as arquivo:
        return arquivo.read()