# Dockerfile

FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Requirements kopieren und installieren
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Rest des Codes kopieren
COPY . .

# Port für FastAPI (Standard: 8000)
EXPOSE 8000

# Startbefehl
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-exclude", ".venv", "--reload-exclude", "database"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
