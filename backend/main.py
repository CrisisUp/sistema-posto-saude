from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(title="Sistema do Posto de Saúde - Arquitetura Limpa")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Injeta todas as rotas modulares que configuramos no arquivo routes.py
app.include_router(router)