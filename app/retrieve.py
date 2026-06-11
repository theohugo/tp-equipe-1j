"""
R3 - Retrieval
Recherche top-k dans Qdrant + seuil de similarité (refus sous le seuil).

Livrable : retrieve.py fonctionnel + section "Retrieval" du compte rendu
"""
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.store import QdrantStore

_model: SentenceTransformer | None = None
_store: QdrantStore | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embed_model)
    return _model


def get_store() -> QdrantStore:
    global _store
    if _store is None:
        _store = QdrantStore()
    return _store


def retrieve(query: str) -> tuple[list[dict], bool]:
    """
    Vectorise la question, cherche les top_k chunks, applique le seuil.

    Returns:
        (chunks, refused)
        - chunks : liste des résultats Qdrant (avec 'score', 'text', 'source', ...)
        - refused : True si le meilleur score est sous le seuil (pas de contexte fiable)

    TODO R3 :
        1. Encoder la query avec get_model()
        2. Appeler get_store().search(vector, top_k)
        3. Si results est vide ou results[0]['score'] < threshold → refused=True
    """
    model = get_model()
    store = get_store()

    query_vector = model.encode(query, normalize_embeddings=True).tolist()

    results = store.search(query_vector, top_k=settings.top_k)

    if not results or results[0]["score"] < settings.similarity_threshold:
        return [], True

    return results, False
