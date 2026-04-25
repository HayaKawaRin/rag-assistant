import re
from difflib import SequenceMatcher

from app.db.models import DocumentChunk
from app.core.config import settings


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)

    text = re.sub(r"O\(1\)O\(1\)", "O(1)", text)
    text = re.sub(r"O\(n\)O\(n\)", "O(n)", text)
    text = re.sub(r"O\(nlog[^\s]*n\)O\(nlogn\)", "O(n log n)", text)
    text = re.sub(r"O\(n2\)O\(n2\)", "O(n^2)", text)

    return text.strip()


def trim_broken_start(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    if re.match(r"^[A-ZА-Я0-9]", text):
        return text

    sentence_start = re.search(r"(?<!\w)([A-ZА-Я][^.!?]{20,})", text)
    if sentence_start:
        return sentence_start.group(1).strip()

    candidates = list(re.finditer(r"(?<=[.!?])\s+([A-ZА-Я])", text))
    if candidates:
        start_index = candidates[0].start(1)
        return text[start_index:].strip()

    return text


def trim_broken_end(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    if text.endswith((".", "!", "?")):
        return text

    last_dot = max(text.rfind("."), text.rfind("!"), text.rfind("?"))
    if last_dot > 100:
        return text[: last_dot + 1].strip()

    return text


def remove_repeated_tail(text: str) -> str:
    if not text:
        return ""

    words = text.split()
    n = len(words)

    for size in range(min(120, n // 2), 20, -1):
        first = " ".join(words[:size])
        rest = " ".join(words[size:])
        if first and first in rest:
            return first.strip()

    return text


def lexical_overlap_ratio(a: str, b: str) -> float:
    a_words = set(re.findall(r"\w+", a.lower()))
    b_words = set(re.findall(r"\w+", b.lower()))

    if not a_words or not b_words:
        return 0.0

    intersection = len(a_words & b_words)
    base = min(len(a_words), len(b_words))
    if base == 0:
        return 0.0

    return intersection / base


def are_near_duplicates(a: str, b: str) -> bool:
    if not a or not b:
        return False

    seq_ratio = SequenceMatcher(None, a, b).ratio()
    overlap_ratio = lexical_overlap_ratio(a, b)

    return seq_ratio >= 0.82 or overlap_ratio >= 0.88


def deduplicate_chunk_texts(chunks: list[DocumentChunk]) -> list[str]:
    unique_texts: list[str] = []

    for chunk in chunks:
        cleaned = normalize_text(chunk.chunk_text)
        cleaned = trim_broken_start(cleaned)
        cleaned = trim_broken_end(cleaned)

        if len(cleaned) < 80:
            continue

        is_duplicate = any(are_near_duplicates(cleaned, existing) for existing in unique_texts)
        if not is_duplicate:
            unique_texts.append(cleaned)

    return unique_texts


def build_context(chunks: list[DocumentChunk], max_chars: int | None = None) -> str:
    max_chars = max_chars or settings.max_context_chars

    parts = []
    total = 0

    unique_texts = deduplicate_chunk_texts(chunks)

    for cleaned in unique_texts:
        if total + len(cleaned) > max_chars:
            remaining = max_chars - total
            if remaining > 150:
                clipped = trim_broken_end(cleaned[:remaining])
                if clipped:
                    parts.append(clipped)
            break

        parts.append(cleaned)
        total += len(cleaned) + 2

    return "\n\n".join(parts).strip()


def build_answer(context_chunks: list[DocumentChunk], max_chars: int | None = None) -> str:
    max_chars = max_chars or settings.max_answer_chars

    unique_texts = deduplicate_chunk_texts(context_chunks)

    if not unique_texts:
        return "I could not find enough relevant information in the uploaded documents."

    full_context = " ".join(unique_texts).strip()
    full_context = trim_broken_start(full_context)
    full_context = trim_broken_end(full_context)
    full_context = remove_repeated_tail(full_context)

    if not full_context:
        return "I found relevant content, but it was too fragmented to assemble into a clean answer."

    if len(full_context) <= max_chars:
        return full_context

    cutoff = trim_broken_end(full_context[:max_chars])
    if len(cutoff) >= 200:
        return cutoff

    return full_context[:max_chars].rstrip() + "..."