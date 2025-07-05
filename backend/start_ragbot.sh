#!/bin/bash

# Pfad zur externen .env-Datei
# example:
#     OPENAI_API_KEY=sk-...
#     ALLOWED_CLIENTS=firma1:abc123,firma2:123abc
ENV_FILE="../../path/to/.env"

# Prüfen, ob .env existiert
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Fehler: .env-Datei nicht gefunden unter $ENV_FILE"
    exit 1
fi

# Alle Variablen aus der externen .env-Datei exportieren
set -o allexport
source "$ENV_FILE"
set +o allexport

# Testausgabe: Prüfen ob ALLOWED_CLIENTS korrekt gesetzt wurde
echo "✅ ALLOWED_CLIENTS: $ALLOWED_CLIENTS"

# Docker Compose starten
docker compose up --build -d
