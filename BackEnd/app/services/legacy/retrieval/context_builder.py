# import re

# from sqlalchemy.orm import Session, joinedload

# from app.db.models import DocumentChunk


# def trim_broken_start(text: str) -> str:
#     if not text:
#         return ""

#     text = text.strip()

#     if re.match(r"^[A-ZА-Я0-9]", text):
#         return text

#     candidates = list(re.finditer(r"(?<=[.!?])\s+([A-ZА-Я])", text))
#     if candidates:
#         start_index = candidates[0].start(1)
#         return text[start_index:].strip()

#     fallback = re.search(r"\b([A-ZА-Я][a-zа-яA-ZА-Я0-9].{20,})", text)
#     if fallback:
#         return fallback.group(1).strip()

#     return text


# def remove_repeated_tail(text: str) -> str:
#     if not text:
#         return ""

#     words = text.split()
#     n = len(words)

#     for size in range(min(120, n // 2), 20, -1):
#         first = " ".join(words[:size])
#         rest = " ".join(words[size:])
#         if first and first in rest:
#             return first.strip()

#     return text


# def normalize_text(text: str) -> str:
#     if not text:
#         return ""

#     text = text.replace("\r", " ").replace("\n", " ")
#     text = re.sub(r"\s+", " ", text)
#     text = re.sub(r"\s+([,.!?;:])", r"\1", text)

#     text = re.sub(r"O\(1\)O\(1\)", "O(1)", text)
#     text = re.sub(r"O\(n\)O\(n\)", "O(n)", text)
#     text = re.sub(r"O\(nlog[^\s]*n\)O\(nlogn\)", "O(n log n)", text)
#     text = re.sub(r"O\(n2\)O\(n2\)", "O(n^2)", text)

#     return text.strip()


# def expand_best_chunk(db: Session, best_chunk: DocumentChunk, window: int = 1) -> list[DocumentChunk]:
#     neighbors = (
#         db.query(DocumentChunk)
#         .options(joinedload(DocumentChunk.document))
#         .filter(
#             DocumentChunk.document_id == best_chunk.document_id,
#             DocumentChunk.chunk_index >= best_chunk.chunk_index - window,
#             DocumentChunk.chunk_index <= best_chunk.chunk_index + window,
#         )
#         .order_by(DocumentChunk.chunk_index.asc())
#         .all()
#     )
#     return neighbors


# def build_context(chunks: list[DocumentChunk], max_chars: int = 3000) -> str:
#     parts = []
#     total = 0

#     for row in chunks:
#         cleaned = normalize_text(row.chunk_text)
#         if not cleaned:
#             continue

#         if total + len(cleaned) > max_chars:
#             remaining = max_chars - total
#             if remaining > 150:
#                 parts.append(cleaned[:remaining])
#             break

#         parts.append(cleaned)
#         total += len(cleaned) + 1

#     return "\n\n".join(parts).strip()