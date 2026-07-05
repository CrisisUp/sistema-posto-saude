from fastapi import WebSocket
from typing import List

class GerenciadorTV:
    """Gerencia o canal de comunicação em tempo real com as TVs via WebSocket."""
    def __init__(self):
        # Mantemos o nome padronizado para bater com as rotas
        self.conexoes: List[WebSocket] = []

    async def conectar(self, websocket: WebSocket):
        await websocket.accept()
        self.conexoes.append(websocket)

    def desconectar(self, websocket: WebSocket):
        if websocket in self.conexoes:
            self.conexoes.remove(websocket)

    async def enviar_chamada_tv(self, nome_paciente: str, sala: str):
        if not self.conexoes:
            return
        payload = {"nome": nome_paciente, "sala": sala}
        # Transmite em broadcast para todas as TVs conectadas na mesma instância de memória
        for conexao in list(self.conexoes):
            try:
                await conexao.send_json(payload)
            except Exception:
                self.desconectar(conexao)

# ==============================================================================
# 🚨 PADRÃO SINGLETON: CRIA A INSTÂNCIA ÚNICA GLOBAL COMPARTILHADA
# ==============================================================================
gerenciador_tv = GerenciadorTV()