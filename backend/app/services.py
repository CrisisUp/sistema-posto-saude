from fastapi import WebSocket
from typing import List

class GerenciadorTV:
    """Gerencia o canal de comunicação em tempo real com as TVs via WebSocket."""
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