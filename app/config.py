from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    groq_api_key: str = ""
    gemini_api_key: str = ""
    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"

    # Vector store
    vector_store: str = "qdrant"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "assistkb"

    # Embeddings
    embed_model: str = "all-MiniLM-L6-v2"
    embed_dim: int = 384

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 120

    # Retrieval
    top_k: int = 5
    similarity_threshold: float = 0.45

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
