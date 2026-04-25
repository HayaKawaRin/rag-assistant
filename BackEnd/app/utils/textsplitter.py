import re


def normalize_whitespace(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_sentences(text: str) -> list[str]:
    if not text:
        return []

    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZА-Я])", text)
    return [p.strip() for p in parts if p.strip()]


def split_long_sentence(sentence: str, max_len: int) -> list[str]:
    if len(sentence) <= max_len:
        return [sentence]

    parts = re.split(r"(?<=,|;|:)\s+", sentence)
    chunks = []
    current = ""

    for part in parts:
        candidate = f"{current} {part}".strip() if current else part
        if len(candidate) <= max_len:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = part

    if current:
        chunks.append(current)

    return chunks


def chunk_paragraph(paragraph: str, chunk_size: int, overlap: int) -> list[str]:
    sentences = split_into_sentences(paragraph)
    if not sentences:
        return []

    processed_sentences = []
    for sentence in sentences:
        if len(sentence) > chunk_size:
            processed_sentences.extend(split_long_sentence(sentence, chunk_size))
        else:
            processed_sentences.append(sentence)

    chunks = []
    current = []

    for sentence in processed_sentences:
        candidate = " ".join(current + [sentence]).strip()

        if len(candidate) <= chunk_size:
            current.append(sentence)
            continue

        if current:
            chunks.append(" ".join(current).strip())

        if overlap > 0 and current:
            carry = []
            total = 0
            for s in reversed(current):
                if total + len(s) > overlap:
                    break
                carry.insert(0, s)
                total += len(s) + 1
            current = carry + [sentence]
        else:
            current = [sentence]

    if current:
        chunks.append(" ".join(current).strip())

    return [c for c in chunks if c]


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    text = normalize_whitespace(text)
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks = []

    for paragraph in paragraphs:
        if len(paragraph) <= chunk_size:
            chunks.append(paragraph)
        else:
            chunks.extend(chunk_paragraph(paragraph, chunk_size, overlap))

    merged = []
    buffer = ""

    for chunk in chunks:
        candidate = f"{buffer}\n\n{chunk}".strip() if buffer else chunk

        if len(candidate) <= chunk_size:
            buffer = candidate
        else:
            if buffer:
                merged.append(buffer.strip())
            buffer = chunk

    if buffer:
        merged.append(buffer.strip())

    cleaned = []
    seen = set()

    for chunk in merged:
        chunk = chunk.strip()
        if len(chunk) < 80:
            continue
        if chunk in seen:
            continue
        cleaned.append(chunk)
        seen.add(chunk)

    return cleaned