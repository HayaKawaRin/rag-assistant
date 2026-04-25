from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.document import DocumentListItem, DocumentUploadResponse
from app.services.document_service import (
    upload_document as upload_document_service,
    list_documents as list_documents_service,
    delete_document as delete_document_service,
)

router = APIRouter()


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        result = upload_document_service(db, file)
        await file.close()
        return result
    except ValueError as e:
        await file.close()
        message = str(e)

        if message == "Only PDF files are allowed.":
            raise HTTPException(status_code=415, detail=message)

        raise HTTPException(status_code=400, detail=message)


@router.get("/documents", response_model=list[DocumentListItem])
def list_documents(db: Session = Depends(get_db)):
    return list_documents_service(db)


@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    try:
        return delete_document_service(db, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))