from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.services.chat_service import (
    handle_chat,
    list_chat_sessions,
    list_session_messages,
    delete_session,
)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: int | None = None


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return handle_chat(db, current_user.id, payload.message, payload.session_id)


@router.get("/chat/sessions")
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_chat_sessions(db, current_user.id)


@router.get("/chat/sessions/{session_id}/messages")
def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return list_session_messages(db, session_id, current_user.id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")


@router.delete("/chat/sessions/{session_id}")
def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return delete_session(db, session_id, current_user.id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")