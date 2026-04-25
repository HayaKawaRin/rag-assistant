# from sqlalchemy.orm import Session

# from app.db.repositories.chat_repository import ChatRepository
# from app.services.retrieval.answer_service import build_answer, build_sources
# from app.services.retrieval.context_builder import build_context, expand_best_chunk
# from app.services.retrieval.vector_search_service import search_similar_chunks


# def get_or_create_session(repo: ChatRepository, session_id: int | None, question: str):
#     if session_id is None:
#         return repo.create_session(question[:50])

#     session = repo.get_session_by_id(session_id)
#     if session:
#         return session

#     return repo.create_session(question[:50])


# def save_message(
#     repo: ChatRepository,
#     session_id: int,
#     role: str,
#     content: str,
#     sources: list[dict] | None = None,
# ):
#     return repo.create_message(
#         session_id=session_id,
#         role=role,
#         content=content,
#         sources=sources,
#     )


# def handle_chat(db: Session, question: str, session_id: int | None = None) -> dict:
#     repo = ChatRepository(db)

#     question = question.strip()

#     if not question:
#         return {
#             "session_id": session_id or 0,
#             "answer": "Please enter a question.",
#             "sources": [],
#             "context_preview": "",
#         }

#     session = get_or_create_session(repo, session_id, question)
#     save_message(repo, session.id, "user", question)

#     search_results, ordered_chunks = search_similar_chunks(db, question, top_k=3)

#     if not search_results:
#         answer = "No indexed document found. Please upload a PDF first."
#         save_message(repo, session.id, "assistant", answer, [])
#         return {
#             "session_id": session.id,
#             "answer": answer,
#             "sources": [],
#             "context_preview": "",
#         }

#     if not ordered_chunks:
#         answer = "Relevant vector results were found, but chunk records are missing in the database."
#         save_message(repo, session.id, "assistant", answer, [])
#         return {
#             "session_id": session.id,
#             "answer": answer,
#             "sources": [],
#             "context_preview": "",
#         }

#     best_chunk = ordered_chunks[0]
#     expanded_chunks = expand_best_chunk(db, best_chunk, window=1)

#     context = build_context(expanded_chunks)
#     answer = build_answer(question, expanded_chunks)

#     chunk_map = {row.id: row for row in ordered_chunks}
#     sources = build_sources(search_results, chunk_map)

#     save_message(repo, session.id, "assistant", answer, sources)

#     return {
#         "session_id": session.id,
#         "answer": answer,
#         "sources": sources,
#         "context_preview": context,
#     }


# def list_chat_sessions(db: Session) -> list[dict]:
#     repo = ChatRepository(db)
#     sessions = repo.list_sessions()

#     return [
#         {
#             "id": s.id,
#             "title": s.title,
#             "created_at": s.created_at.isoformat(),
#         }
#         for s in sessions
#     ]


# def list_session_messages(db: Session, session_id: int) -> list[dict]:
#     repo = ChatRepository(db)
#     messages = repo.list_messages(session_id)

#     return [
#         {
#             "id": m.id,
#             "role": m.role,
#             "content": m.content,
#             "sources": m.sources or [],
#             "created_at": m.created_at.isoformat(),
#         }
#         for m in messages
#     ]


# def delete_session(db: Session, session_id: int) -> dict:
#     repo = ChatRepository(db)
#     chat_session = repo.get_session_by_id(session_id)

#     if not chat_session:
#         raise ValueError("Session not found")

#     repo.delete_session(chat_session)
#     return {"ok": True, "message": "Session deleted"}