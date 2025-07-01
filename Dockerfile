# Dockerfile

FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Rest des Codes kopieren
COPY . .

# Port für FastAPI (Standard: 8000)
EXPOSE 8000

# Startbefehl
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-exclude", ".venv", "--reload_exclude", "database"]
