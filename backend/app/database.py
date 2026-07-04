import sqlite3
from app.config import DB_PATH

class DatabaseConnection:
    """Gerenciador central de conexões com o banco de dados SQLite."""
    @staticmethod
    def obter_conexao() -> sqlite3.Connection:
        conexao = sqlite3.connect(DB_PATH)
        conexao.row_factory = sqlite3.Row
        return conexao