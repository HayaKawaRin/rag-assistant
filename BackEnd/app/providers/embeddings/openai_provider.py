from openai import OpenAI

from app.core.config import settings
from app.providers.embeddings.base import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=getattr(settings, "openai_base_url", None) or None,
        )

        self.model = (
            getattr(settings, "embedding_model", None)
            or getattr(settings, "embedding_model_name", None)
            or "text-embedding-3-small"
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]


embedding_provider = OpenAIEmbeddingProvider()