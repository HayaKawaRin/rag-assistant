from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: int | None = None


class ChatSource(BaseModel):
    filename: str
    score: float


class ChatResponse(BaseModel):
    session_id: int
    answer: str
    sources: list[ChatSource] = []
    context_preview: str = ""