#!/bin/bash

ENV_FILE="../../../private_data/.env"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Fehler: .env-Datei nicht gefunden unter $ENV_FILE"
    exit 1
fi

set -o allexport
source "$ENV_FILE"
set +o allexport

echo "✅ ALLOWED_CLIENTS: $ALLOWED_CLIENTS"

# Schritt 1: Temporäre Config verwenden
echo "🌐 Starte temporäres Nginx für Certbot..."
cp nginx/certbot.conf nginx/default.conf
docker compose up -d nginx

sleep 5

# # change here to correct DOMAIN
echo "🔍 Prüfe ob Zertifikat im Volume vorhanden ist..."
docker run --rm -v certbot-etc:/etc/letsencrypt alpine sh -c \
    '[ -f /etc/letsencrypt/live/api.camillo-dobrovsky.de/fullchain.pem ]' && CERT_EXISTS=true || CERT_EXISTS=false
if [ "$CERT_EXISTS" = false ]; then

    echo "🔐 Kein Zertifikat gefunden. Starte Certbot... $CERT_PATH"
    docker run --rm \
        -v certbot-etc:/etc/letsencrypt \
        -v certbot-var:/var/lib/letsencrypt \
        -v "$(pwd)/webroot:/var/www/html" \
        certbot/certbot certonly \
        --webroot \
        --webroot-path=/var/www/html \
        --email deine@mail.de \
        --agree-tos \
        --no-eff-email \
        -d api.camillo-dobrovsky.de

    if [ $? -ne 0 ]; then
        echo "❌ Certbot fehlgeschlagen. Abbruch."
        exit 1
    fi
    echo "✅ Zertifikat erfolgreich erstellt."
else
    echo "✅ Zertifikat bereits vorhanden unter $CERT_PATH"
fi

# Schritt 2: Finales HTTPS-Nginx konfigurieren
echo "🔄 Wechsle zu produktiver HTTPS-Konfiguration..."
cp nginx/https.conf nginx/default.conf

# Schritt 3: Alles neu starten
docker compose down
sleep 5
docker compose up -d --build

echo "✅ RAGBot läuft"
