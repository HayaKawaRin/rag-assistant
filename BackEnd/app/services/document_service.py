from pathlib import Path
import shutil
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.repositories.document_repository import DocumentRepository
from app.services.embedding_service import get_embeddings
from app.services.rag_service import rag_store
from app.utils.pdfparser import extract_text_from_pdf
from app.utils.textsplitter import chunk_text


settings.uploads_path.mkdir(parents=True, exist_ok=True)


def upload_document(db: Session, file) -> dict:
    if file.content_type != "application/pdf":
        raise ValueError("Only PDF files are allowed.")

    if not file.filename:
        raise ValueError("File must have a name.")

    suffix = Path(file.filename).suffix or ".pdf"
    unique_name = f"{uuid.uuid4().hex}{suffix}"
    file_path = settings.uploads_path / unique_name

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    parsed = extract_text_from_pdf(str(file_path))
    full_text = parsed["full_text"]

    chunks = chunk_text(full_text, chunk_size=1000, overlap=150)

    if not chunks:
        if file_path.exists():
            file_path.unlink()
        raise ValueError("No text could be extracted from PDF.")

    repo = DocumentRepository(db)

    document = repo.create_document(
        filename=file.filename,
        file_path=str(file_path),
        page_count=parsed["page_count"],
        text_length=len(full_text),
    )

    chunk_rows = repo.create_chunks(document.id, chunks)

    embeddings = get_embeddings(chunks)
    chunk_ids = [row.id for row in chunk_rows]
    rag_store.add_embeddings(embeddings, chunk_ids)

    repo.set_faiss_positions(chunk_rows)

    return {
        "document_id": document.id,
        "filename": document.filename,
        "stored_file": str(file_path),
        "page_count": document.page_count,
        "text_length": document.text_length,
        "chunk_count": len(chunk_rows),
        "preview": full_text[:500],
    }


def list_documents(db: Session) -> list[dict]:
    repo = DocumentRepository(db)
    documents = repo.list_documents()

    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "page_count": doc.page_count,
            "text_length": doc.text_length,
            "created_at": doc.created_at.isoformat(),
            "chunk_count": len(doc.chunks),
        }
        for doc in documents
    ]


def delete_document(db: Session, document_id: int) -> dict:
    repo = DocumentRepository(db)
    document = repo.get_document_by_id(document_id)

    if not document:
        raise ValueError("Document not found.")

    chunk_ids = [chunk.id for chunk in document.chunks]

    removed_vectors = 0
    if chunk_ids:
        removed_vectors = rag_store.remove_embeddings(chunk_ids)

    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()

    repo.delete_document(document)

    return {
        "ok": True,
        "message": "Document deleted successfully.",
        "document_id": document_id,
        "removed_chunks": len(chunk_ids),
        "removed_vectors": removed_vectors,
    }