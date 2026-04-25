from sqlalchemy.orm import Session

from app.db.models import ChatSession, Message


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_session_by_id(self, session_id: int, user_id: int) -> ChatSession | None:
        return (
            self.db.query(ChatSession)
            .filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
            .first()
        )

    def create_session(self, user_id: int, title: str) -> ChatSession:
        session = ChatSession(
            user_id=user_id,
            title=title,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def create_message(
        self,
        session_id: int,
        role: str,
        content: str,
        sources: list[dict] | None = None,
    ) -> Message:
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def list_sessions(self, user_id: int) -> list[ChatSession]:
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

    def list_messages(self, session_id: int, user_id: int) -> list[Message]:
        session = self.get_session_by_id(session_id, user_id)
        if not session:
            return []

        return (
            self.db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    def delete_session(self, session: ChatSession) -> None:
        self.db.delete(session)
        self.db.commit()