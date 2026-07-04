from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import List
from fastapi.responses import HTMLResponse

app = FastAPI(title="Sistema do Posto de Saúde")

# CONFIGURAÇÃO DE SEGURANÇA (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "../banco/posto_saude.db"

# --- GERENCIADOR DE CONEXÕES DA TV (WEBSOCKET) ---
class GerenciadorTV:
    def __init__(self):
        # Guarda todas as TVs conectadas na rede local
        self.conexoes_ativas: List[WebSocket] = []

    async def conectar(self, websocket: WebSocket):
        await websocket.accept()
        self.conexoes_ativas.append(websocket)

    def desconectar(self, websocket: WebSocket):
        if websocket in self.conexoes_ativas:
            self.conexoes_ativas.remove(websocket)

    async def enviar_chamada_tv(self, nome_paciente: str, sala: str):
        # Se não houver nenhuma TV ligada, ignora o envio e evita travar o backend
        if not self.conexoes_ativas:
            return

        payload = {"nome": nome_paciente, "sala": sala}
        # Cria uma cópia da lista para evitar erros de modificação durante o loop
        for conexao in list(self.conexoes_ativas):
            try:
                await conexao.send_json(payload)
            except Exception:
                # Se a conexão caiu ou falhou, remove da lista e segue em frente
                self.desconectar(conexao)

gerenciador_tv = GerenciadorTV()

# --- MODELO DE VALIDAÇÃO (Recepção) ---
class PacienteCadastro(BaseModel):
    nome_paciente: str
    documento_unico: str
    nome_mae: str
    data_nascimento: str  
    gravidade: int        
    especialidade_id: int 

@app.get("/")
def rota_inicial():
    return {"status": "Servidor do Posto de Saúde está online!"}

# --- ROTA DA RECEPÇÃO: CADASTRAR PACIENTE ---
@app.post("/recepcao/cadastrar")
def cadastrar_paciente(paciente: PacienteCadastro):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO atendimentos (nome_paciente, documento_unico, nome_mae, data_nascimento, gravidade, status, especialidade_id)
            VALUES (?, ?, ?, ?, ?, 'AGUARDANDO', ?)
        """, (paciente.nome_paciente, paciente.documento_unico, paciente.nome_mae, paciente.data_nascimento, paciente.gravidade, paciente.especialidade_id))
        conn.commit()
        conn.close()
        return {"status": "sucesso", "mensagem": f"Paciente {paciente.nome_paciente} inserido na fila!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# --- ROTAS DO MÉDICO ---

# 1. Buscar o próximo paciente da fila ordenado por prioridade
@app.get("/medico/proximo/{especialidade_id}")
def buscar_proximo_paciente(especialidade_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *, 
                   (strftime('%Y', 'now') - strftime('%Y', data_nascimento) >= 60) AS eh_idoso
            FROM atendimentos
            WHERE status = 'AGUARDANDO' AND especialidade_id = ?
            ORDER BY gravidade DESC, eh_idoso DESC, criado_em ASC
            LIMIT 1
        """, (especialidade_id,))
        proximo = cursor.fetchone()
        conn.close()
        
        if proximo:
            return dict(proximo)
        return {"mensagem": "Nenhum paciente aguardando nesta fila."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar próximo: {str(e)}")

# 2. Alterar o status do paciente para CHAMADO, capturar a sala dinâmica e avisar a TV
@app.post("/medico/chamar/{atendimento_id}")
async def chamar_paciente(atendimento_id: int, sala: str = None):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Atualiza o status no banco de dados
        cursor.execute("UPDATE atendimentos SET status = 'CHAMADO', chamado_em = CURRENT_TIMESTAMP WHERE id = ?", (atendimento_id,))
        
        # Busca o nome do paciente e a sala padrão (como backup se não receber parâmetro)
        cursor.execute("""
            SELECT a.nome_paciente, e.sala 
            FROM atendimentos a
            JOIN especialidades e ON a.especialidade_id = e.id
            WHERE a.id = ?
        """, (atendimento_id,))
        dados = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        if dados:
            # Se o frontend enviou a sala na URL (ex: "2"), formata para "Consultório 2".
            # Se não enviou, usa o que está cadastrado na tabela de especialidades.
            sala_final = dados["sala"]
            if sala:
                sala_final = sala if "Consultório" in sala else f"Consultório {sala}"

            # DISPARO PROTEGIDO: Envia os dados corretos para a TV
            try:
                await gerenciador_tv.enviar_chamada_tv(dados["nome_paciente"], sala_final)
            except Exception:
                pass
            return {"status": "sucesso", "mensagem": f"Paciente chamado no painel!"}
        
        return {"status": "erro", "mensagem": "Atendimento não encontrado."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao chamar: {str(e)}")

# --- CANAL WEBSOCKET QUE A TV VAI SE CONECTAR ---
@app.websocket("/ws/tv")
async def websocket_tv_endpoint(websocket: WebSocket):
    await gerenciador_tv.conectar(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        gerenciador_tv.desconectar(websocket)

# Rota para abrir a tela do médico de forma profissional e segura
@app.get("/tela-medico", response_class=HTMLResponse)
def abrir_tela_medico():
    with open("medico.html", "r", encoding="utf-8") as arquivo:
        return arquivo.read()
    
# Rota para abrir o painel da TV da sala de espera
@app.get("/tela-tv", response_class=HTMLResponse)
def abrir_tela_tv():
    with open("tv.html", "r", encoding="utf-8") as arquivo:
        return arquivo.read()
    
# 3. Mudar status para FINALIZADO ou resetar para AGUARDANDO (Fim da fila se ausente)
@app.post("/medico/status/{atendimento_id}")
def alterar_status_atendimento(atendimento_id: int, acao: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if acao == "INICIAR":
            cursor.execute("UPDATE atendimentos SET status = 'EM_ATENDIMENTO' WHERE id = ?", (atendimento_id,))
        
        elif acao == "FINALIZAR":
            cursor.execute("UPDATE atendimentos SET status = 'FINALIZADO' WHERE id = ?", (atendimento_id,))
            
        elif acao == "AUSENTE":
            # A MÁGICA AQUI: Voltamos para AGUARDANDO e atualizamos o 'criado_em' para a hora atual.
            # Como a busca usa 'ORDER BY criado_em ASC', ele vai direto para o fim da fila da prioridade dele!
            cursor.execute("""
                UPDATE atendimentos 
                SET status = 'AGUARDANDO', 
                    criado_em = CURRENT_TIMESTAMP,
                    chamado_em = NULL 
                WHERE id = ?
            """, (atendimento_id,))
            
        conn.commit()
        conn.close()
        return {"status": "sucesso", "mensagem": f"Ação {acao} processada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao alterar status: {str(e)}")