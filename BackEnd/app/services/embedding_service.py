from functools import lru_cache

from app.core.config import settings


@lru_cache
def get_local_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model_name)


@lru_cache
def get_openai_client():
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    from openai import OpenAI
    return OpenAI(api_key=settings.openai_api_key)


def _clean_text(text: str) -> str:
    return text.replace("\n", " ").strip()


def _get_local_embeddings(texts: list[str]) -> list[list[float]]:
    model = get_local_model()
    cleaned_texts = [_clean_text(text) for text in texts]

    embeddings = model.encode(
        cleaned_texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings.tolist()


def _get_openai_embeddings(texts: list[str]) -> list[list[float]]:
    client = get_openai_client()
    cleaned_texts = [_clean_text(text) for text in texts]

    response = client.embeddings.create(
        model=settings.openai_embedding_model,
        input=cleaned_texts,
    )

    ordered = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in ordered]


def get_embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    provider = settings.embedding_provider.lower()

    if provider == "local":
        return _get_local_embeddings(texts)

    if provider == "openai":
        return _get_openai_embeddings(texts)

    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")


def get_query_embedding(text: str) -> list[float]:
    embeddings = get_embeddings([text])
    if not embeddings:
        raise ValueError("Failed to generate query embedding.")
    return embeddings[0]


def get_embedding_provider_info() -> dict:
    provider = settings.embedding_provider.lower()

    if provider == "local":
        return {
            "provider": "local",
            "model": settings.embedding_model_name,
        }

    if provider == "openai":
        return {
            "provider": "openai",
            "model": settings.openai_embedding_model,
        }

    return {
        "provider": provider,
        "model": "unknown",
    }