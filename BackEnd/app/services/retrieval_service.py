import re
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import DocumentChunk
from app.db.repositories.document_repository import DocumentRepository
from app.services.embedding_service import get_query_embedding
from app.services.rag_service import rag_store


MIN_SCORE_THRESHOLD = 0.12
DENSE_WEIGHT = 0.75
LEXICAL_WEIGHT = 0.25


def tokenize(text: str) -> list[str]:
    if not text:
        return []
    return re.findall(r"[a-zA-Zа-яА-Я0-9_]+", text.lower())


def lexical_overlap_score(query: str, text: str) -> float:
    query_tokens = set(tokenize(query))
    text_tokens = set(tokenize(text))

    if not query_tokens or not text_tokens:
        return 0.0

    overlap = len(query_tokens & text_tokens)
    return overlap / len(query_tokens)


def search_similar_chunks(
    db: Session,
    question: str,
    top_k: int | None = None,
) -> tuple[list[dict], list[DocumentChunk]]:
    top_k = top_k or settings.top_k

    query_embedding = get_query_embedding(question)
    raw_results = rag_store.search(query_embedding, top_k=top_k * 8)

    if not raw_results:
        return [], []

    repo = DocumentRepository(db)

    candidate_ids = [item["chunk_id"] for item in raw_results if float(item["score"]) >= MIN_SCORE_THRESHOLD]
    if not candidate_ids:
        return [], []

    chunk_rows = repo.get_chunks_by_ids(candidate_ids)
    chunk_map = {row.id: row for row in chunk_rows}

    reranked = []

    for item in raw_results:
        chunk_id = item["chunk_id"]
        dense_score = float(item["score"])

        chunk = chunk_map.get(chunk_id)
        if not chunk:
            continue

        lexical_score = lexical_overlap_score(question, chunk.chunk_text)
        combined_score = (dense_score * DENSE_WEIGHT) + (lexical_score * LEXICAL_WEIGHT)

        reranked.append({
            "chunk_id": chunk_id,
            "score": dense_score,
            "lexical_score": round(lexical_score, 4),
            "combined_score": round(combined_score, 4),
        })

    reranked.sort(key=lambda x: x["combined_score"], reverse=True)

    unique_results = []
    seen_ids = set()

    for item in reranked:
        if item["chunk_id"] in seen_ids:
            continue
        unique_results.append(item)
        seen_ids.add(item["chunk_id"])

    final_results = unique_results[:top_k]
    retrieved_ids = [item["chunk_id"] for item in final_results]
    ordered_chunks = [chunk_map[cid] for cid in retrieved_ids if cid in chunk_map]

    return final_results, ordered_chunks


def expand_best_chunk(
    db: Session,
    best_chunk: DocumentChunk,
    window: int | None = None,
) -> list[DocumentChunk]:
    window = settings.chunk_expand_window if window is None else window
    repo = DocumentRepository(db)
    return repo.get_neighbor_chunks(best_chunk.document_id, best_chunk.chunk_index, window)


def gather_parent_context(
    db: Session,
    best_chunk: DocumentChunk,
    radius: int = 1,
) -> list[DocumentChunk]:
    repo = DocumentRepository(db)
    return repo.get_neighbor_chunks(
        document_id=best_chunk.document_id,
        chunk_index=best_chunk.chunk_index,
        window=radius,
    )


def build_sources(results: list[dict], chunk_rows: list[DocumentChunk]) -> list[dict]:
    if not results or not chunk_rows:
        return []

    chunk_map = {row.id: row for row in chunk_rows}
    unique_files = {}

    for item in results:
        chunk = chunk_map.get(item["chunk_id"])
        if not chunk:
            continue

        filename = chunk.document.filename if chunk.document else "Unknown file"
        score = round(float(item.get("combined_score", item["score"])), 3)

        if filename not in unique_files or score > unique_files[filename]["score"]:
            unique_files[filename] = {
                "filename": filename,
                "score": score,
            }

    return list(unique_files.values())[:3]