from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # <-- NOVO IMPORT
from app.routes import router
import os

app = FastAPI(title="Sistema do Posto de Saúde - Arquitetura Limpa")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NOVO: Diz ao FastAPI para servir a pasta 'static' no endereço '/static' ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Injeta todas as rotas modulares
app.include_router(router)