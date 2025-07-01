import os
import shutil

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from ragbot.ragbot import RAGBot

#print(load_dotenv())

allowed_firmen = os.getenv("ALLOWED_CLIENTS")
# allowed_firmen = "testfirma1,testfirma2"
allowed_firmen_set = set(f.strip().lower() for f in allowed_firmen.split(",") if f.strip())

# ------------------- #
# Variables
# ------------------- #
database_path = "./database"
document_dir = "./ragbot/docs/"

# -------------------- #
# Initialisierung
# -------------------- #

app = FastAPI()
limiter_global = Limiter(key_func=get_remote_address)  # IP-basiert
limiter_firma = Limiter(key_func=lambda r: get_firma_key(r))  # Firmenbasiert

app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter_global

# -------------------- #
# Instanz des RAG-Bots
# -------------------- #
if not os.path.exists(database_path):
    os.makedirs(database_path)
else:
    print("Found existing DB, overwriting")
    shutil.rmtree(database_path)
    os.makedirs(database_path)
bot = RAGBot(docs_path=document_dir, db_dir=database_path)


# -------------------- #
# Rate-Limit Key für Firmen
# -------------------- #

def get_firma_key(request: Request) -> str:
    try:
        body = request._json  # wird von slowapi gesetzt
        firma = body.get("firma", "").strip().lower()
        if not firma:
            return "firma:unbekannt"
        return f"firma:{firma}"
    except Exception:
        return "firma:fehler"


# -------------------- #
# Fehlerbehandlung
# -------------------- #

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    key = get_firma_key(request)
    if key.startswith("firma:"):
        msg = "Leider ist das Limit für diese Firma in dieser Stunde erreicht."
    else:
        msg = "Leider ist das globale Anfrage-Limit für diese Stunde erreicht."
    return JSONResponse(status_code=429, content={"answer": msg})


# -------------------- #
# Endpunkte
# -------------------- #

@app.get("/")
def root():
    return {"message": "RAGBot API ist online!"}


@app.post("/chat")
@limiter_global.limit("10/hour")
@limiter_firma.limit("3/hour")
async def chat(request: Request):
    body = await request.json()
    question = body.get("query", "").strip()
    firma = body.get("firma", "").strip().lower()

    if not question or not firma:
        return JSONResponse(status_code=400, content={"error": "Bitte 'query' und 'firma' angeben."})

    if firma not in allowed_firmen_set:
        return JSONResponse(status_code=403, content={"error": "Firma nicht autorisiert."})

    answer = bot.call_chat(question)
    return {"answer": answer}
