from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RAG Assistant API"
    cors_origins: list[str] = ["http://localhost:5173"]

    database_url: str = "sqlite:///ragassistant.db"

    embedding_provider: str = "local"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_api_key: str | None = None

    generation_provider: str = "extractive"
    openai_chat_model: str = "gpt-4o-mini"

    storage_dir: str = "storage"
    uploads_dir: str = "storage/uploads"
    faiss_dir: str = "storage/faiss"
    faiss_index_path: str = "storage/faiss/documents.index"

    top_k: int = 3
    chunk_expand_window: int = 1
    max_context_chars: int = 3000
    max_answer_chars: int = 2200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def uploads_path(self) -> Path:
        return Path(self.uploads_dir)

    @property
    def faiss_index_file(self) -> Path:
        return Path(self.faiss_index_path)


settings = Settings()