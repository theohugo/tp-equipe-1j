#!/bin/bash
set -e

# Ingestion — seulement si chunks.jsonl est absent ou vide
if [ ! -s corpus/chunks.jsonl ]; then
    echo "[start] Ingestion du corpus..."
    python -m app.ingest
else
    echo "[start] corpus/chunks.jsonl déjà présent, ingestion ignorée."
fi

# Embedding — vérifie si la collection Qdrant est déjà peuplée
POINTS=$(curl -sf "http://${QDRANT_HOST:-qdrant}:${QDRANT_PORT:-6333}/collections/${QDRANT_COLLECTION:-assistkb}" 2>/dev/null \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('points_count',0))" 2>/dev/null || echo "0")

if [ "$POINTS" = "0" ]; then
    echo "[start] Indexation dans Qdrant..."
    python -m app.embed
else
    echo "[start] Qdrant déjà peuplé ($POINTS vecteurs), indexation ignorée."
fi

echo "[start] Démarrage de l'API..."
exec uvicorn app.api:app --host 0.0.0.0 --port 8000
