from fastapi import FastAPI, HTTPException
from rd_station import RDStationAPI
from typing import Optional
import os

app = FastAPI(title="RD Station API", description="API para Copilot Studio")

# Instância global da API
rd_api = RDStationAPI()

@app.get("/")
def home():
    """Endpoint de teste"""
    return {
        "status": "online",
        "message": "API RD Station funcionando!"
    }

@app.get("/campanhas")
def get_campanhas(data_inicio: Optional[str] = None, data_fim: Optional[str] = None):
    """
    Retorna campanhas de email
    
    Parâmetros:
    - data_inicio: formato YYYY-MM-DD (opcional)
    - data_fim: formato YYYY-MM-DD (opcional)
    """
    try:
        dados = rd_api.get_campanhas_email(data_inicio, data_fim)
        return {
            "success": True,
            "data": dados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Verifica se o token está válido"""
    try:
        token_valido = rd_api.is_token_valid()
        return {
            "status": "healthy",
            "token_valid": token_valido
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
