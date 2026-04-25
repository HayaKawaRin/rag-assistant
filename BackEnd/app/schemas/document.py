from pydantic import BaseModel


class DocumentListItem(BaseModel):
    id: int
    filename: str
    page_count: int
    text_length: int
    created_at: str
    chunk_count: int


class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    stored_file: str
    page_count: int
    text_length: int
    chunk_count: int
    preview: str