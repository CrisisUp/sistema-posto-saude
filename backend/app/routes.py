import os
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Optional
from app.repositories import AtendimentoRepository, PacienteCadastro
# 🚨 ALTERADO: Importando a instância global gerenciador_tv em minúsculo
from app.services import gerenciador_tv 
from app.config import TEMPLATES_DIR

# O APIRouter do FastAPI permite criar rotas em arquivos separados e injetá-las no app principal
router = APIRouter()

repository = AtendimentoRepository()

# 🚨 REMOVIDO: gerenciador_tv = GerenciadorTV() 
# Agora usamos a instância única vinda do services para unificar as memórias!

@router.get("/")
def index():
    return {"status": "Servidor do Posto de Saúde está online!"}

@router.post("/recepcao/cadastrar")
def cadastrar(paciente: PacienteCadastro):
    try:
        repository.inserir_na_fila(paciente)
        return {"status": "sucesso", "mensagem": f"Paciente {paciente.nome_paciente} inserido!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medico/proximo/{especialidade_id}")
def proximo(especialidade_id: int):
    paciente = repository.buscar_proximo_da_fila(especialidade_id)
    if not paciente:
        return {"mensagem": "Nenhum paciente aguardando nesta fila."}
    return paciente

@router.post("/medico/chamar/{atendimento_id}")
async def chamar(atendimento_id: int, sala: str):
    nome_paciente = repository.atualizar_status_e_obter_nome(atendimento_id, sala)
    if not nome_paciente:
        return {"status": "erro", "mensagem": "Atendimento não encontrado."}
    
    sala_final = sala if sala and "Consultório" in sala else f"Consultório {sala or '1'}"
    
    # Adicionando um print temporário para debug sênior no terminal
    print(f"--- BROADCAST: Enviando para {len(gerenciador_tv.conexoes)} TVs na memória ---")
    
    await gerenciador_tv.enviar_chamada_tv(nome_paciente, sala_final)
    return {"status": "sucesso", "mensagem": "Paciente chamado!"}

@router.post("/medico/status/{atendimento_id}")
def status(atendimento_id: int, acao: str):
    repository.executar_transicao_de_status(atendimento_id, acao)
    return {"status": "sucesso"}

@router.websocket("/ws/tv")
async def websocket_tv(websocket: WebSocket):
    # Aceita a conexão da TV na instância unificada
    await gerenciador_tv.conectar(websocket)
    print(f"--- TV CONECTADA: Total de TVs ativas = {len(gerenciador_tv.conexoes)} ---")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        gerenciador_tv.desconectar(websocket)
        print("--- TV DESCONECTADA ---")

# Rotas de renderização atualizadas para buscar na pasta templates/
@router.get("/tela-medico", response_class=HTMLResponse)
def tela_medico():
    with open(os.path.join(TEMPLATES_DIR, "medico.html"), "r", encoding="utf-8") as f:
        return f.read()

@router.get("/tela-tv", response_class=HTMLResponse)
def tela_tv():
    with open(os.path.join(TEMPLATES_DIR, "tv.html"), "r", encoding="utf-8") as f:
        return f.read()
    
@router.get("/medico/ultima-chamada")
def obter_ultima_chamada():
    ultimo = repository.obter_ultimo_chamado()
    if not ultimo:
        return {"mensagem": "Nenhuma chamada ativa no momento"}

    # Pega a sala que ficou salva no banco! Se estiver nula, assume Consultório 1
    sala_salva = ultimo.get("sala_atendimento") or "1"

    return {
        "nome": ultimo["nome_paciente"],
        "sala": f"Consultório {sala_salva}"
    }