import re

from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.db.models import FlashcardCard, FlashcardDeck


KZ_SPECIFIC = set("әғқңөұүһі")
RU_COMMON = {
    "это", "что", "как", "если", "или", "так", "его", "она", "они", "для",
    "при", "может", "который", "также", "однако", "между", "потому"
}
KZ_COMMON = {
    "және", "үшін", "бұл", "бір", "бар", "болып", "ретінде", "оның", "мен",
    "да", "де", "ма", "ме", "қалай", "қандай", "бірақ", "сияқты"
}
EN_COMMON = {
    "the", "and", "is", "are", "for", "with", "that", "this", "can", "will",
    "from", "into", "about", "because", "between", "students", "education"
}


def _normalize_text(text: str) -> str:
    text = text.replace("\r", " ").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", _normalize_text(text))
    if not text:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _truncate(text: str, max_len: int = 180) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _clean_answer(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _detect_language(text: str) -> str:
    lowered = text.lower()

    if any(ch in lowered for ch in KZ_SPECIFIC):
        return "KZ"

    latin_chars = sum(1 for ch in lowered if "a" <= ch <= "z")
    cyrillic_chars = sum(1 for ch in lowered if "а" <= ch <= "я" or ch == "ё")

    words = re.findall(r"[a-zA-Zа-яА-ЯёЁәғқңөұүһі]+", lowered)

    kz_score = sum(1 for word in words if word in KZ_COMMON)
    ru_score = sum(1 for word in words if word in RU_COMMON)
    en_score = sum(1 for word in words if word in EN_COMMON)

    if latin_chars > cyrillic_chars:
        return "ENG"
    if kz_score > ru_score:
        return "KZ"
    if ru_score >= kz_score:
        return "RUS"
    return "ENG"


def _extract_key_cards(sentences: list[str], count: int, language: str) -> list[dict]:
    cards = []

    for sentence in sentences:
        clean = sentence.strip()
        if len(clean) < 35:
            continue

        if ":" in clean and len(cards) < count:
            left, right = clean.split(":", 1)
            left = left.strip()
            right = right.strip()

            if left and right and len(left.split()) <= 8:
                if language == "RUS":
                    question = f"Что такое {left}?"
                elif language == "KZ":
                    question = f"{left} деген не?"
                else:
                    question = f"What is {left}?"

                cards.append({
                    "question": question,
                    "answer": _clean_answer(right),
                })
                continue

        lowered = clean.lower()

        if " is " in lowered and language == "ENG" and len(cards) < count:
            parts = re.split(r"\bis\b", clean, maxsplit=1, flags=re.IGNORECASE)
            if len(parts) == 2:
                subject = parts[0].strip(" ,.-")
                definition = parts[1].strip(" ,.-")
                if subject and definition and len(subject.split()) <= 8:
                    cards.append({
                        "question": f"What is {subject}?",
                        "answer": _clean_answer(definition),
                    })
                    continue

        if len(cards) < count:
            if language == "RUS":
                question = f"Что говорится о следующем: {_truncate(clean, 80)}?"
            elif language == "KZ":
                question = f"Мына туралы не айтылған: {_truncate(clean, 80)}?"
            else:
                question = f"What does the text say about: {_truncate(clean, 80)}?"

            cards.append({
                "question": question,
                "answer": _clean_answer(clean),
            })

        if len(cards) >= count:
            break

    return cards[:count]


def _fallback_flashcards(title: str, text: str, count: int, language: str) -> dict:
    sentences = _split_sentences(text)

    if not sentences:
        return {
            "deck_title": title or "My Flashcard Deck",
            "language": language,
            "cards": [],
        }

    cards = _extract_key_cards(sentences, count, language)

    if not cards:
        if language == "RUS":
            question = "Какая главная идея в этом материале?"
        elif language == "KZ":
            question = "Бұл материалдың негізгі идеясы қандай?"
        else:
            question = "What is the main idea of this study material?"

        cards = [{
            "question": question,
            "answer": _truncate(_normalize_text(text), 220),
        }]

    return {
        "deck_title": title or "My Flashcard Deck",
        "language": language,
        "cards": cards[:count],
    }


def _openai_flashcards(title: str, text: str, count: int, language: str) -> dict:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)

    lang_instruction = {
        "RUS": "Generate the flashcards in Russian.",
        "KZ": "Generate the flashcards in Kazakh.",
        "ENG": "Generate the flashcards in English.",
    }[language]

    system_prompt = (
        "You are an educational flashcard generator. "
        "Turn the user's study material into concise flashcards for active recall. "
        "Each card must contain exactly one clear question and one short answer. "
        "Keep each card focused on one idea only. "
        "Avoid combining multiple facts in a single card. "
        f"{lang_instruction} "
        "Return the result in exactly this format:\n\n"
        "DECK_TITLE:\n"
        "<deck title>\n\n"
        "CARDS:\n"
        "Q: <question 1>\n"
        "A: <answer 1>\n"
        "Q: <question 2>\n"
        "A: <answer 2>\n"
    )

    user_prompt = f"""
Deck title: {title}
Target number of cards: {count}
Detected language: {language}

Study material:
{text}
"""

    response = client.responses.create(
        model=settings.openai_chat_model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    output = response.output_text.strip()

    deck_title = title or "My Flashcard Deck"
    cards = []

    deck_match = re.search(r"DECK_TITLE:\s*(.+?)(?:\n|$)", output, re.DOTALL)
    if deck_match:
        deck_title = deck_match.group(1).strip()

    lines = [line.strip() for line in output.splitlines() if line.strip()]
    current_question = None

    for line in lines:
        if line.startswith("Q:"):
            current_question = line[2:].strip()
        elif line.startswith("A:") and current_question:
            answer = line[2:].strip()
            if current_question and answer:
                cards.append({
                    "question": current_question,
                    "answer": answer,
                })
            current_question = None

    return {
        "deck_title": deck_title,
        "language": language,
        "cards": cards[:count],
    }


def create_flashcard_deck(
    db: Session,
    user_id: int,
    title: str,
    text: str,
    count: int = 5,
) -> FlashcardDeck:
    safe_title = title.strip() if title else "My Flashcard Deck"
    language = _detect_language(text)

    result = None
    if settings.openai_api_key:
        try:
            result = _openai_flashcards(safe_title, text, count, language)
            if not result.get("cards"):
                result = None
        except Exception:
            result = None

    if result is None:
        result = _fallback_flashcards(safe_title, text, count, language)

    deck = FlashcardDeck(
        user_id=user_id,
        deck_title=result["deck_title"],
        language=result["language"],
    )
    db.add(deck)
    db.flush()

    for idx, card in enumerate(result["cards"]):
        db.add(
            FlashcardCard(
                deck_id=deck.id,
                question=card["question"],
                answer=card["answer"],
                position=idx,
            )
        )

    db.commit()

    return (
        db.query(FlashcardDeck)
        .options(selectinload(FlashcardDeck.cards))
        .filter(
            FlashcardDeck.id == deck.id,
            FlashcardDeck.user_id == user_id,
        )
        .first()
    )


def list_flashcard_decks(db: Session, user_id: int) -> list[FlashcardDeck]:
    return (
        db.query(FlashcardDeck)
        .options(selectinload(FlashcardDeck.cards))
        .filter(FlashcardDeck.user_id == user_id)
        .order_by(FlashcardDeck.id.desc())
        .all()
    )


def delete_flashcard_deck(db: Session, deck_id: int, user_id: int) -> bool:
    deck = (
        db.query(FlashcardDeck)
        .filter(
            FlashcardDeck.id == deck_id,
            FlashcardDeck.user_id == user_id,
        )
        .first()
    )
    if not deck:
        return False

    db.delete(deck)
    db.commit()
    return True


def delete_flashcard_card(
    db: Session,
    deck_id: int,
    card_id: int,
    user_id: int,
) -> FlashcardDeck | None:
    deck = (
        db.query(FlashcardDeck)
        .options(selectinload(FlashcardDeck.cards))
        .filter(
            FlashcardDeck.id == deck_id,
            FlashcardDeck.user_id == user_id,
        )
        .first()
    )
    if not deck:
        return None

    card = (
        db.query(FlashcardCard)
        .filter(
            FlashcardCard.id == card_id,
            FlashcardCard.deck_id == deck_id,
        )
        .first()
    )
    if not card:
        return None

    db.delete(card)
    db.commit()

    return (
        db.query(FlashcardDeck)
        .options(selectinload(FlashcardDeck.cards))
        .filter(
            FlashcardDeck.id == deck_id,
            FlashcardDeck.user_id == user_id,
        )
        .first()
    )