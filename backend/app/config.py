import os

# Caminho absoluto para a pasta 'backend' (onde o servidor roda)
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Caminho para o banco (sobe um nível a partir de backend e entra na pasta banco)
DB_PATH = os.path.abspath(os.path.join(BACKEND_DIR, "../banco/posto_saude.db"))

# Caminho para a pasta templates
TEMPLATES_DIR = os.path.abspath(os.path.join(BACKEND_DIR, "templates"))