import os
import re
import shutil

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from ragbot.ragbot import RAGBot
from starlette.middleware.cors import CORSMiddleware

codes_str = os.getenv("ALLOWED_CLIENTS", "")

if not codes_str:
    codes_str = "testcompany:1234"
allowed_codes = dict()
for item in codes_str.split(","):
    if ":" in item:
        company, code = item.split(":", 1)
        if company.strip():
            allowed_codes[company.strip().lower()] = code.strip() if code.strip() else "default"
# ------------------- #
# Variables
# ------------------- #
database_path = "./database"
document_dir = "./ragbot/docs"
use_ragbot_per_company = True

# -------------------- #
# Rate-Limit Key for companies
# -------------------- #

def get_company_key(request: Request) -> str:
    try:
        body = request._json
        comp = body.get("company", "").strip().lower()
        if not comp:
            return "company:unknown"
        return f"company:{comp}"
    except Exception:
        return "company:fehler"

# -------------------- #
# init
# -------------------- #

limiter_company = Limiter(key_func=get_company_key)

app = FastAPI()

app.state.limiter = limiter_company
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://camillo-dobrovsky.de"],     # DOMAIN of frontend or *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# -------------------- #
# ragbot instantiation
# -------------------- #
if use_ragbot_per_company:
    company_bots = dict()
    del_comps = []
    for company in allowed_codes.keys():
        c_database_path = os.path.join(database_path, company)
        c_document_dir = os.path.join(document_dir, company)
        if not os.path.exists(c_document_dir):
            print(f"WARNING: Didn't found company {company}. Removing from allowed client-list")
            del_comps.append(company)
            continue
        if not os.path.exists(c_database_path):
            os.makedirs(c_database_path)
        else:
            print(f"Found existing DB for {company}, overwriting")
            shutil.rmtree(c_database_path)
            os.makedirs(c_database_path)
        print(f"Init Ragbot for company {company}")
        company_bots[company] = RAGBot(docs_path=c_document_dir, db_dir=c_database_path)
    for comp in del_comps:
        del allowed_codes[comp]
else:
    if not os.path.exists(database_path):
        os.makedirs(database_path)
    else:
        print("Found existing DB, overwriting")
        shutil.rmtree(database_path)
        os.makedirs(database_path)
    print("Init Ragbot")
    bot = RAGBot(docs_path=document_dir, db_dir=database_path)
print("Finished RAGBot init")

def extract_html_content(response_text: str) -> str:
    codeblock_match = re.search(r"```html\s*(.*?)\s*```", response_text, re.DOTALL)
    if codeblock_match:
        return codeblock_match.group(1).strip()

    html_like_match = re.search(r"(<(html|div|section|table|ul|ol|p|span|h1|h2|h3|h4|h5|h6)[\s>].*?)$", response_text, re.DOTALL | re.IGNORECASE)
    if html_like_match:
        return html_like_match.group(1).strip()

    return response_text.strip()

# -------------------- #
# errorhandling
# -------------------- #

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    key = get_company_key(request)
    if key.startswith("company:"):
        msg = "Jede Anfrage an die OpenAI-API kostet Geld, wenn auch nur wenig. Leider musste Camillo, welcher aktuell noch armer Student ist, deswegen ein Anfragelimit setzen. Dieses ist aktuell erreicht, wird aber alle 24 h zurückgesetzt."
    else:
        msg = "Jede Anfrage an die OpenAI-API kostet Geld, wenn auch nur wenig. Leider konnte Camillo, welcher aktuell noch armer Student ist, nicht unbegrenzt Geld auf sein OpenAI-Account einzahlen. Dieses Geld scheint nun aufgebraucht zu sein."
    return JSONResponse(status_code=429, content={"answer": msg})


# -------------------- #
# endpoints
# -------------------- #

@app.get("/")
def root():
    return {"message": "RAGBot API ist online!"}


@app.post("/chat")
@limiter_company.limit("20/day")
async def chat(request: Request):
    body = await request.json()
    question = body.get("query", "").strip()
    comp = body.get("company", "").strip().lower()
    code = body.get("code", "").strip()
    salutation = body.get("salutation", "Siezen").strip()
    user_name = body.get("username", "").strip()

    if not question or not comp:
        return JSONResponse(status_code=400, content={"error": "Bitte 'query' und 'firma' angeben."})

    if not allowed_codes.get(comp, False) or allowed_codes.get(comp) != code:
        return JSONResponse(status_code=403, content={"error": "Nicht autorisierter Zugriff. Bitte Firma & Code in der URL überprüfen."})

    if use_ragbot_per_company:
        answer = company_bots[comp].call_chat(question, salutation, user_name)
    else:
        answer = bot.call_chat(question, salutation, user_name)
    return {"answer": extract_html_content(answer)}
