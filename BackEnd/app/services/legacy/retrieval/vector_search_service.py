# from sqlalchemy.orm import Session, joinedload

# from app.db.models import DocumentChunk
# from app.services.embedding_service import get_query_embedding
# from app.services.retrieval.vector_store import rag_store


# def search_similar_chunks(db: Session, question: str, top_k: int = 3) -> tuple[list[dict], list[DocumentChunk]]:
#     query_embedding = get_query_embedding(question)
#     search_results = rag_store.search(query_embedding, top_k=top_k)

#     if not search_results:
#         return [], []

#     retrieved_ids = [item["chunk_id"] for item in search_results]

#     chunk_rows = (
#         db.query(DocumentChunk)
#         .options(joinedload(DocumentChunk.document))
#         .filter(DocumentChunk.id.in_(retrieved_ids))
#         .all()
#     )

#     chunk_map = {row.id: row for row in chunk_rows}
#     ordered_chunks = [chunk_map[cid] for cid in retrieved_ids if cid in chunk_map]

#     return search_results, ordered_chunks