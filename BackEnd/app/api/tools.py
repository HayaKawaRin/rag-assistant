from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.models import User
from app.db.database import get_db
from app.schemas.tools import (
    DeleteResponse,
    EssayRequest,
    EssayResponse,
    FlashcardDeckListResponse,
    FlashcardRequest,
    FlashcardResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from app.services.essay_service import process_essay_request
from app.services.flashcard_service import (
    create_flashcard_deck,
    delete_flashcard_card,
    delete_flashcard_deck,
    list_flashcard_decks,
)
from app.services.summarizer_service import summarize_text


router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(payload: SummarizeRequest):
    try:
        result = summarize_text(payload.text, payload.length)
        return SummarizeResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to summarize text.")


@router.post("/essay", response_model=EssayResponse)
def essay_helper(payload: EssayRequest):
    try:
        result = process_essay_request(
            text=payload.text,
            mode=payload.mode,
            level=payload.level,
        )
        return EssayResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process essay request.")


@router.post("/flashcards", response_model=FlashcardResponse)
def flashcards(
    payload: FlashcardRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = create_flashcard_deck(
            db=db,
            user_id=current_user.id,
            title=payload.title,
            text=payload.text,
            count=payload.count,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {str(exc)}")


@router.get("/flashcards", response_model=FlashcardDeckListResponse)
def get_flashcard_decks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        decks = list_flashcard_decks(db, current_user.id)
        return {"decks": decks}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load flashcard decks.")


@router.delete("/flashcards/{deck_id}", response_model=DeleteResponse)
def remove_flashcard_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deleted = delete_flashcard_deck(db, deck_id, current_user.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Deck not found.")
        return {"message": "Deck deleted successfully."}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete flashcard deck.")


@router.delete("/flashcards/{deck_id}/cards/{card_id}", response_model=FlashcardResponse)
def remove_flashcard_card(
    deck_id: int,
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deck = delete_flashcard_card(db, deck_id, card_id, current_user.id)
        if deck is None:
            raise HTTPException(status_code=404, detail="Deck or card not found.")
        return deck
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete flashcard card.")