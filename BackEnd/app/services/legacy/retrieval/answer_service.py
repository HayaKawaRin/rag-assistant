# from app.db.models import DocumentChunk
# from app.services.retrieval.context_builder import (
#     normalize_text,
#     trim_broken_start,
#     remove_repeated_tail,
# )


# def build_sources(results: list[dict], chunk_map: dict[int, DocumentChunk]) -> list[dict]:
#     if not results:
#         return []

#     best_result = max(results, key=lambda x: x["score"])
#     best_chunk = chunk_map.get(best_result["chunk_id"])

#     if not best_chunk:
#         return []

#     filename = best_chunk.document.filename if best_chunk.document else "Unknown file"

#     return [
#         {
#             "filename": filename,
#             "score": round(float(best_result["score"]), 3),
#         }
#     ]


# def build_answer(question: str, context_chunks: list[DocumentChunk]) -> str:
#     if not context_chunks:
#         return "I could not find enough relevant information in the uploaded documents."

#     cleaned_parts = [normalize_text(chunk.chunk_text) for chunk in context_chunks if chunk.chunk_text]
#     full_context = " ".join(part for part in cleaned_parts if part).strip()

#     if not full_context:
#         return "I found a relevant document, but could not extract a clean explanation from it."

#     full_context = trim_broken_start(full_context)
#     full_context = remove_repeated_tail(full_context)

#     if len(full_context) <= 2200:
#         return full_context

#     cutoff = full_context[:2200]
#     last_dot = max(cutoff.rfind("."), cutoff.rfind("!"), cutoff.rfind("?"))

#     if last_dot > 500:
#         return cutoff[:last_dot + 1]

#     return cutoff + "..."