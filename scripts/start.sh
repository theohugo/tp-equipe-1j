#!/bin/bash
set -e

if [ ! -s corpus/chunks.jsonl ]; then
    echo "[start] Ingestion du corpus..."
    python -m app.ingest
else
    echo "[start] corpus/chunks.jsonl deja present, ingestion ignoree."
fi

POINTS=$(curl -sf "http://${QDRANT_HOST:-qdrant}:${QDRANT_PORT:-6333}/collections/${QDRANT_COLLECTION:-assistkb}" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('points_count',0))" 2>/dev/null || echo "0")

if [ "$POINTS" = "0" ]; then
    echo "[start] Indexation dans Qdrant..."
    python -m app.embed
else
    echo "[start] Qdrant deja peuple ($POINTS vecteurs), indexation ignoree."
fi

echo "[start] Demarrage de l'API..."
exec uvicorn app.api:app --host 0.0.0.0 --port 8000