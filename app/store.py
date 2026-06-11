"""
R2 - QdrantStore
Adaptateur pour créer la collection et faire les upsert / search dans Qdrant.
"""
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from app.config import settings


class QdrantStore:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self.collection = settings.qdrant_collection

    def init_collection(self) -> None:
        """Crée la collection si elle n'existe pas (idempotent)."""
        existing = [c.name for c in self.client.get_collections().collections]
        if self.collection not in existing:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=settings.embed_dim,
                    # TODO R2 : choisir la distance (cosinus recommandé avec vecteurs normalisés)
                    distance=Distance.COSINE,
                ),
            )
            print(f"Collection '{self.collection}' créée (dim={settings.embed_dim})")
        else:
            print(f"Collection '{self.collection}' déjà existante")

    def upsert(self, vectors: list[list[float]], chunks: list[dict]) -> None:
        """
        TODO R2 : insérer les vecteurs + payloads dans Qdrant.
        Vérifier l'idempotence : relancer ne duplique pas.
        Conseil : utiliser chunk_index + source comme id stable (hash ou compteur global).
        """
        points = []
        for i, (vec, chunk) in enumerate(zip(vectors, chunks)):
            # TODO R2 : générer un id stable (ex: hash sur source+chunk_index)
            point_id = hash(f"{chunk['source']}_{chunk['chunk_index']}") % (2**31)
            points.append(
                PointStruct(
                    id=abs(point_id),
                    vector=vec,
                    payload=chunk,
                )
            )
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, query_vector: list[float], top_k: int) -> list[dict]:
        """
        Recherche les top_k chunks les plus proches du vecteur requête.
        Retourne une liste de dicts avec 'score' et les métadonnées du chunk.
        """
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
        )
        return [
            {"score": r.score, **r.payload}
            for r in results
        ]
