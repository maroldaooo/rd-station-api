import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional
from rd_station import RDStationAPI

# -------------------------------
# Instância da aplicação
# -------------------------------
app = FastAPI(
    title="RD Station Proxy API",
    description="Proxy entre Copilot Studio e RD Station",
    version="1.0.0"
)

# -------------------------------
# Variáveis de ambiente
# -------------------------------
rd_api = RDStationAPI()  # instância da API RD Station
PROXY_API_KEY = os.getenv("PROXY_API_KEY")  # chave secreta do proxy
API_KEY_HEADER = os.getenv("API_KEY_HEADER_NAME", "X-API-KEY")  # nome do header

# -------------------------------
# Middleware para autenticação
# -------------------------------
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    # Rotas públicas
    if request.url.path in ["/", "/health"]:
        return await call_next(request)

    # Verifica se o header existe e bate com a chave do Render
    if PROXY_API_KEY:
        header_key = request.headers.get(API_KEY_HEADER)
        # Log para depuração
        print(f"[DEBUG] Header recebido: {header_key}")
        print(f"[DEBUG] Chave do Render: {PROXY_API_KEY}")
        if not header_key or header_key != PROXY_API_KEY:
            return JSONResponse(
                status_code=403,
                content={"error": "Acesso negado. Chave de API inválida."}
            )

    return await call_next(request)

# -------------------------------
# Endpoints públicos
# -------------------------------
@app.get("/")
def home():
    """Endpoint de teste"""
    return {
        "status": "online",
        "message": "API RD Station funcionando e protegida com X-API-KEY"
    }

@app.get("/health")
def health_check():
    """Verifica se o token do RD Station está válido"""
    try:
        token_valido = rd_api.is_token_valid()
        return {"status": "healthy", "token_valid": token_valido}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# -------------------------------
# Endpoints protegidos
# -------------------------------
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

# -------------------------------
# Ponto de entrada (Render usa Gunicorn)
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
