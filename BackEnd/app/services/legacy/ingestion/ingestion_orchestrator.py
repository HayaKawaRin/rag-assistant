# from sqlalchemy.orm import Session

# from app.db.models import Document, DocumentChunk
# from app.services.ingestion.extract_service import extract_text
# from app.services.ingestion.cleaning_service import clean_text
# from app.services.ingestion.chunking_service import split_into_chunks
# from app.services.ingestion.embedding_service import embed_chunks
# from app.services.ingestion.indexing_service import indexing_service


# def ingest_document(
#     db: Session,
#     file_path: str,
#     filename: str,
# ) -> dict:
#     raw_text = extract_text(file_path)
#     cleaned_text = clean_text(raw_text)
#     chunks = split_into_chunks(cleaned_text)

#     if not chunks:
#         raise ValueError("No text chunks were created from the uploaded document.")

#     document = Document(filename=filename, file_path=file_path)
#     db.add(document)
#     db.flush()

#     chunk_rows = []
#     for idx, chunk_text in enumerate(chunks):
#         chunk_row = DocumentChunk(
#             document_id=document.id,
#             chunk_index=idx,
#             chunk_text=chunk_text,
#         )
#         db.add(chunk_row)
#         chunk_rows.append(chunk_row)

#     db.flush()

#     embeddings = embed_chunks([row.chunk_text for row in chunk_rows])
#     chunk_ids = [row.id for row in chunk_rows]

#     indexing_service.add_embeddings(embeddings, chunk_ids)
#     db.commit()

#     return {
#         "document_id": document.id,
#         "filename": document.filename,
#         "chunks_count": len(chunk_rows),
#     }