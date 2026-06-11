"""
R2 - Embeddings / Index
Vectoriser les chunks et peupler Qdrant.

Livrable : Qdrant peuplé + section "Index / Embeddings" du compte rendu
"""
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

from app.config import settings
from app.store import QdrantStore

CHUNKS_IN = Path("corpus/chunks.jsonl")
BATCH_SIZE = 64


def load_chunks() -> list[dict]:
    if not CHUNKS_IN.exists():
        raise FileNotFoundError(f"{CHUNKS_IN} introuvable — lancez d'abord ingest.py")
    with CHUNKS_IN.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_embedding() -> int:
    """Vectorise les chunks et les upserte dans Qdrant. Retourne le nb de vecteurs."""
    chunks = load_chunks()
    print(f"{len(chunks)} chunks à vectoriser")

    # TODO R2 : instancier le modèle d'embeddings
    # model = SentenceTransformer(settings.embed_model)

    store = QdrantStore()
    store.init_collection()

    total = 0
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        texts = [c["text"] for c in batch]

        # TODO R2 : produire les vecteurs (normaliser avec normalize_embeddings=True)
        # vectors = model.encode(texts, normalize_embeddings=True).tolist()

        # TODO R2 : upsert dans Qdrant via store.upsert(vectors, batch)
        # store.upsert(vectors, batch)

        total += len(batch)
        print(f"  Batch {i // BATCH_SIZE + 1} — {total}/{len(chunks)} chunks indexés")

    print(f"Indexation terminée : {total} vecteurs dans la collection '{settings.qdrant_collection}'")
    return total


if __name__ == "__main__":
    run_embedding()
