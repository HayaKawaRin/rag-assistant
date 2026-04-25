from sqlalchemy.orm import Session

from app.db.repositories.chat_repository import ChatRepository
from app.services.answer_service import build_context
from app.services.generation_service import generate_answer
from app.services.retrieval_service import (
    search_similar_chunks,
    expand_best_chunk,
    gather_parent_context,
    build_sources,
)


def get_or_create_session(
    repo: ChatRepository,
    user_id: int,
    session_id: int | None,
    question: str,
):
    if session_id is None:
        return repo.create_session(user_id=user_id, title=question[:50])

    session = repo.get_session_by_id(session_id, user_id)
    if session:
        return session

    return repo.create_session(user_id=user_id, title=question[:50])


def save_message(
    repo: ChatRepository,
    session_id: int,
    role: str,
    content: str,
    sources: list[dict] | None = None,
):
    return repo.create_message(
        session_id=session_id,
        role=role,
        content=content,
        sources=sources,
    )


def handle_chat(
    db: Session,
    user_id: int,
    question: str,
    session_id: int | None = None,
) -> dict:
    repo = ChatRepository(db)

    question = question.strip()

    if not question:
        return {
            "session_id": session_id or 0,
            "answer": "Please enter a question.",
            "sources": [],
            "context_preview": "",
        }

    session = get_or_create_session(repo, user_id, session_id, question)
    save_message(repo, session.id, "user", question)

    search_results, ordered_chunks = search_similar_chunks(db, question)

    if not search_results:
        answer = "No indexed document found. Please upload a PDF first."
        save_message(repo, session.id, "assistant", answer, [])
        return {
            "session_id": session.id,
            "answer": answer,
            "sources": [],
            "context_preview": "",
        }

    if not ordered_chunks:
        answer = "Relevant vector results were found, but chunk records are missing in the database."
        save_message(repo, session.id, "assistant", answer, [])
        return {
            "session_id": session.id,
            "answer": answer,
            "sources": [],
            "context_preview": "",
        }

    best_chunk = ordered_chunks[0]

    local_chunks = expand_best_chunk(db, best_chunk)
    parent_chunks = gather_parent_context(db, best_chunk, radius=2)

    merged_chunks = []
    seen_ids = set()

    for chunk in local_chunks + parent_chunks:
        if chunk.id not in seen_ids:
            merged_chunks.append(chunk)
            seen_ids.add(chunk.id)

    if not merged_chunks:
        merged_chunks = [best_chunk]

    context_preview = build_context(merged_chunks)
    answer = generate_answer(question, context_preview)
    sources = build_sources(search_results, ordered_chunks)

    save_message(repo, session.id, "assistant", answer, sources)

    return {
        "session_id": session.id,
        "answer": answer,
        "sources": sources,
        "context_preview": context_preview,
    }


def list_chat_sessions(db: Session, user_id: int) -> list[dict]:
    repo = ChatRepository(db)
    sessions = repo.list_sessions(user_id)

    return [
        {
            "id": s.id,
            "title": s.title,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]


def list_session_messages(db: Session, session_id: int, user_id: int) -> list[dict]:
    repo = ChatRepository(db)
    session = repo.get_session_by_id(session_id, user_id)

    if not session:
        raise ValueError("Session not found")

    messages = repo.list_messages(session_id, user_id)

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "sources": m.sources or [],
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


def delete_session(db: Session, session_id: int, user_id: int) -> dict:
    repo = ChatRepository(db)
    chat_session = repo.get_session_by_id(session_id, user_id)

    if not chat_session:
        raise ValueError("Session not found")

    repo.delete_session(chat_session)
    return {"ok": True, "message": "Session deleted"}