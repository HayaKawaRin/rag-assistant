from sqlalchemy.orm import Session, joinedload

from app.db.models import Document, DocumentChunk


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_document(
        self,
        filename: str,
        file_path: str,
        page_count: int,
        text_length: int,
    ) -> Document:
        document = Document(
            filename=filename,
            file_path=file_path,
            page_count=page_count,
            text_length=text_length,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def create_chunks(self, document_id: int, chunks: list[str]) -> list[DocumentChunk]:
        chunk_rows = [
            DocumentChunk(
                document_id=document_id,
                chunk_index=i,
                chunk_text=chunk,
                page_number=None,
            )
            for i, chunk in enumerate(chunks)
        ]

        self.db.add_all(chunk_rows)
        self.db.commit()

        for row in chunk_rows:
            self.db.refresh(row)

        return chunk_rows

    def set_faiss_positions(self, chunk_rows: list[DocumentChunk]) -> None:
        for row in chunk_rows:
            row.faiss_index_position = row.id
        self.db.commit()

    def list_documents(self) -> list[Document]:
        return (
            self.db.query(Document)
            .options(joinedload(Document.chunks))
            .order_by(Document.created_at.desc())
            .all()
        )

    def get_document_by_id(self, document_id: int) -> Document | None:
        return (
            self.db.query(Document)
            .options(joinedload(Document.chunks))
            .filter(Document.id == document_id)
            .first()
        )

    def get_chunks_by_ids(self, chunk_ids: list[int]) -> list[DocumentChunk]:
        return (
            self.db.query(DocumentChunk)
            .options(joinedload(DocumentChunk.document))
            .filter(DocumentChunk.id.in_(chunk_ids))
            .all()
        )

    def get_neighbor_chunks(self, document_id: int, chunk_index: int, window: int) -> list[DocumentChunk]:
        return (
            self.db.query(DocumentChunk)
            .options(joinedload(DocumentChunk.document))
            .filter(
                DocumentChunk.document_id == document_id,
                DocumentChunk.chunk_index >= chunk_index - window,
                DocumentChunk.chunk_index <= chunk_index + window,
            )
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )

    def delete_document(self, document: Document) -> None:
        self.db.delete(document)
        self.db.commit()