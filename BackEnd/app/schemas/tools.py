from typing import Literal

from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=20)
    length: str = Field(default="medium")


class SummarizeResponse(BaseModel):
    summary: str
    key_points: list[str]


class EssayRequest(BaseModel):
    mode: Literal["feedback", "outline", "brainstorm", "improve"]
    text: str = Field(..., min_length=5)
    level: Literal["school", "college", "general"] = "college"


class EssayResponse(BaseModel):
    title: str
    main_text: str
    items: list[str]


class FlashcardItem(BaseModel):
    id: int | None = None
    question: str
    answer: str


class FlashcardRequest(BaseModel):
    title: str = Field(default="My Flashcard Deck")
    text: str = Field(..., min_length=20)
    count: int = Field(default=5, ge=1, le=20)


class FlashcardResponse(BaseModel):
    id: int
    deck_title: str
    language: Literal["RUS", "KZ", "ENG"]
    cards: list[FlashcardItem]

    class Config:
        from_attributes = True


class FlashcardDeckListResponse(BaseModel):
    decks: list[FlashcardResponse]


class DeleteResponse(BaseModel):
    message: str