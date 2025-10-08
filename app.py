from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from rd_station import RDStationAPI
from typing import Optional
import os

# Instância da aplicação
app = FastAPI(
    title="RD Station Proxy API",
    description="Proxy entre Copilot Studio e RD Station",
    version="1.0.0"
)

# Instância global da API RD Station
rd_api = RDStationAPI()

# Leitura da chave de segurança (defina no Render)
PROXY_API_KEY = os.getenv("PROXY_API_KEY")  # ex: "minha-chave-secreta"
API_KEY_HEADER = os.getenv("API_KEY_HEADER_NAME", "X-API-KEY")


# -------------------------------
# Middleware simples para autenticação via header
# -------------------------------
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    # rotas livres (sem necessidade de chave)
    if request.url.path in ["/", "/health"]:
        return await call_next(request)

    if PROXY_API_KEY:
        key = request.headers.get(API_KEY_HEADER)
        if not key or key != PROXY_API_KEY:
            return JSONResponse(
                status_code=403,
                content={"error": "Acesso negado. Chave de API inválida."}
            )

    return await call_next(request)


# -------------------------------
# Endpoints
# -------------------------------

@app.get("/")
def home():
    """Endpoint de teste"""
    return {
        "status": "online",
        "message": "API RD Station funcionando e protegida com X-API-KEY"
    }


@app.get("/campanhas")
def get_campanhas(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None
):
    """
    Retorna campanhas de email do RD Station.
    
    Parâmetros:
    - data_inicio: formato YYYY-MM-DD (opcional)
    - data_fim: formato YYYY-MM-DD (opcional)
    """
    try:
        dados = rd_api.get_campanhas_email(data_inicio, data_fim)
        return {"success": True, "data": dados}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Verifica se o token do RD Station está válido"""
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


# -------------------------------
# Ponto de entrada (Render usa Gunicorn)
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
