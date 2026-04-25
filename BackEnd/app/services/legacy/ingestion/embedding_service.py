# from app.providers.embeddings.openai_provider import embedding_provider


# def embed_chunks(chunks: list[str]) -> list[list[float]]:
#     return embedding_provider.embed(chunks)


# def get_embeddings(texts: list[str]) -> list[list[float]]:
#     return embed_chunks(texts)


# def get_query_embedding(text: str) -> list[float]:
#     vectors = embedding_provider.embed([text])
#     return vectors[0] if vectors else []