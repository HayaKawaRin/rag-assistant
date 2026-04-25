import math
import re
from collections import Counter

from app.core.config import settings


RU_STOPWORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то",
    "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за",
    "бы", "по", "только", "ее", "мне", "было", "вот", "от", "меня", "еще",
    "нет", "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг", "ли",
    "если", "уже", "или", "ни", "быть", "был", "него", "до", "вас", "нибудь",
    "опять", "уж", "вам", "ведь", "там", "потом", "себя", "ничего", "ей",
    "может", "они", "тут", "где", "есть", "надо", "ней", "для", "мы", "тебя",
    "их", "чем", "была", "сам", "чтоб", "без", "будто", "чего", "раз", "тоже",
    "себе", "под", "будет", "ж", "тогда", "кто", "этот", "того", "потому",
    "этого", "какой", "совсем", "ним", "здесь", "этом", "один", "почти", "мой",
    "тем", "чтобы", "нее", "сейчас", "были", "куда", "зачем", "всех", "никогда",
    "можно", "при", "наконец", "два", "об", "другой", "хоть", "после", "над",
    "больше", "тот", "через", "эти", "нас", "про", "всего", "них", "какая",
    "много", "разве", "три", "эту", "моя", "впрочем", "хорошо", "свою", "этой",
    "перед", "иногда", "лучше", "чуть", "том", "нельзя", "такой", "им", "более",
    "всегда", "конечно", "всю", "между"
}

EN_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "when", "at",
    "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "than",
    "once", "here", "there", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "too", "very", "can", "will", "just", "don't", "should",
    "now", "is", "am", "are", "was", "were", "be", "been", "being", "have",
    "has", "had", "do", "does", "did", "of", "as", "it", "its", "this",
    "that", "these", "those", "he", "she", "they", "them", "his", "her",
    "their", "you", "your", "we", "our", "i", "me", "my"
}

STOPWORDS = RU_STOPWORDS | EN_STOPWORDS


def _normalize_text(text: str) -> str:
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _split_sentences(text: str) -> list[str]:
    text = _normalize_text(text)
    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+", text)
    sentences = [p.strip() for p in parts if p.strip()]
    return [s for s in sentences if len(s) >= 40]


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]+", text.lower())


def _content_tokens(text: str) -> list[str]:
    return [t for t in _tokenize(text) if t not in STOPWORDS and len(t) > 2]


def _word_frequencies(sentences: list[str]) -> Counter:
    tokens = []
    for sentence in sentences:
        tokens.extend(_content_tokens(sentence))
    return Counter(tokens)


def _sentence_position_bonus(index: int, total: int) -> float:
    if total <= 1:
        return 0.0

    relative = index / max(total - 1, 1)

    if relative <= 0.10:
        return 0.18
    if relative <= 0.25:
        return 0.08
    if relative >= 0.90:
        return 0.05
    return 0.0


def _lead_sentence_bonus(sentence: str) -> float:
    lowered = sentence.lower()

    patterns = [
        "это",
        "эта",
        "эти",
        "такой",
        "такие",
        "such",
        "this",
        "these",
    ]

    if any(lowered.startswith(p + " ") for p in patterns):
        return -0.18

    return 0.0


def _sentence_score(sentence: str, index: int, total: int, freqs: Counter, top_keywords: set[str]) -> float:
    tokens = _content_tokens(sentence)
    if not tokens:
        return 0.0

    freq_score = sum(freqs.get(token, 0) for token in tokens) / math.sqrt(len(tokens))

    keyword_hits = sum(1 for token in tokens if token in top_keywords)
    keyword_bonus = keyword_hits / max(len(tokens), 1)

    unique_ratio = len(set(tokens)) / max(len(tokens), 1)
    diversity_bonus = unique_ratio * 0.15

    length = len(sentence)
    length_penalty = 0.0
    if length < 60:
        length_penalty -= 0.30
    elif length > 320:
        length_penalty -= 0.12

    position_bonus = _sentence_position_bonus(index, total)
    lead_bonus = _lead_sentence_bonus(sentence)

    return freq_score + keyword_bonus + diversity_bonus + position_bonus + lead_bonus + length_penalty


def _jaccard_similarity(a: str, b: str) -> float:
    a_tokens = set(_content_tokens(a))
    b_tokens = set(_content_tokens(b))

    if not a_tokens or not b_tokens:
        return 0.0

    intersection = len(a_tokens & b_tokens)
    union = len(a_tokens | b_tokens)

    if union == 0:
        return 0.0

    return intersection / union


def _mmr_pick(scored_items: list[tuple[int, str, float]], selected: list[str], lambda_param: float = 0.72):
    best_item = None
    best_value = -10**9

    for idx, sentence, base_score in scored_items:
        if sentence in selected:
            continue

        if not selected:
            mmr_score = base_score
        else:
            max_similarity = max(_jaccard_similarity(sentence, s) for s in selected)
            mmr_score = (lambda_param * base_score) - ((1 - lambda_param) * max_similarity)

        if mmr_score > best_value:
            best_value = mmr_score
            best_item = (idx, sentence, base_score)

    return best_item


def _select_opening_sentence(scored_items: list[tuple[int, str, float]], top_keywords: set[str]) -> tuple[int, str, float] | None:
    candidates = []

    for idx, sentence, score in scored_items:
        tokens = set(_content_tokens(sentence))
        keyword_overlap = len(tokens & top_keywords)
        starts_badly = _lead_sentence_bonus(sentence) < 0

        adjusted = score + (keyword_overlap * 0.08)
        if starts_badly:
            adjusted -= 0.15

        candidates.append((idx, sentence, score, adjusted))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[3], reverse=True)
    idx, sentence, score, _ = candidates[0]
    return idx, sentence, score


def _select_sentences(sentences: list[str], target_count: int) -> tuple[list[str], list[str]]:
    freqs = _word_frequencies(sentences)
    top_keywords = {word for word, _ in freqs.most_common(12)}

    scored = []
    total = len(sentences)

    for idx, sentence in enumerate(sentences):
        score = _sentence_score(sentence, idx, total, freqs, top_keywords)
        scored.append((idx, sentence, score))

    scored.sort(key=lambda x: x[2], reverse=True)

    selected_items = []
    selected_texts = []

    opening = _select_opening_sentence(scored, top_keywords)
    if opening:
        selected_items.append(opening)
        selected_texts.append(opening[1])

    while len(selected_items) < target_count:
        picked = _mmr_pick(scored, selected_texts, lambda_param=0.72)
        if not picked:
            break

        sentence = picked[1]
        if any(_jaccard_similarity(sentence, existing) >= 0.60 for existing in selected_texts):
            break

        selected_items.append(picked)
        selected_texts.append(sentence)

    selected_items.sort(key=lambda x: x[0])
    ordered_selected = [sentence for _, sentence, _ in selected_items]

    ordered_leftovers = []
    selected_set = set(ordered_selected)

    for idx, sentence, score in sorted(scored, key=lambda x: x[0]):
        if sentence not in selected_set:
            ordered_leftovers.append(sentence)

    return ordered_selected[:target_count], ordered_leftovers


def _build_key_points(summary_sentences: list[str], leftovers: list[str]) -> list[str]:
    points = []

    for sentence in leftovers + summary_sentences:
        cleaned = sentence.strip()
        if len(cleaned) < 45:
            continue

        if any(_jaccard_similarity(cleaned, existing) >= 0.65 for existing in points):
            continue

        points.append(cleaned)
        if len(points) >= 5:
            break

    return points


def _extractive_summary(text: str, length: str = "medium") -> dict:
    sentences = _split_sentences(text)

    if not sentences:
        return {
            "summary": "No valid text was provided.",
            "key_points": [],
        }

    target_map = {
        "short": 2,
        "medium": 3,
        "long": 5,
    }
    target_count = target_map.get(length, 3)

    summary_sentences, leftovers = _select_sentences(sentences, target_count)
    summary = " ".join(summary_sentences).strip()
    key_points = _build_key_points(summary_sentences, leftovers)

    return {
        "summary": summary,
        "key_points": key_points,
    }


def _openai_summary(text: str, length: str = "medium") -> dict:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)

    length_map = {
        "short": "Write a short summary in 2-3 sentences.",
        "medium": "Write a medium-length summary in 4-6 sentences.",
        "long": "Write a detailed summary in 6-8 sentences.",
    }
    length_instruction = length_map.get(length, length_map["medium"])

    system_prompt = (
        "You are a helpful summarization assistant. "
        "Read the user's text carefully and produce a clear, human-like summary. "
        "Do not copy large fragments verbatim unless necessary. "
        "Compress the text into its most important ideas. "
        "Then provide 3 to 5 distinct key points that expand coverage instead of repeating the same wording. "
        "If the text contains pros and cons, benefits and risks, or multiple themes, reflect that balance."
    )

    user_prompt = f"""
{length_instruction}

Return the result in exactly this format:

SUMMARY:
<one coherent summary paragraph>

KEY POINTS:
- <point 1>
- <point 2>
- <point 3>

Text:
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

    summary = ""
    key_points = []

    if "KEY POINTS:" in output:
        before, after = output.split("KEY POINTS:", 1)
        summary = before.replace("SUMMARY:", "").strip()

        for line in after.splitlines():
            cleaned = line.strip()
            if cleaned.startswith("-"):
                point = cleaned.lstrip("-").strip()
                if len(point) >= 10:
                    key_points.append(point)
    else:
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        if lines:
            summary = lines[0]
            key_points = lines[1:6]

    deduped_points = []
    for point in key_points:
        if any(_jaccard_similarity(point, existing) >= 0.7 for existing in deduped_points):
            continue
        deduped_points.append(point)

    return {
        "summary": summary or "Could not generate summary.",
        "key_points": deduped_points[:5],
    }


def summarize_text(text: str, length: str = "medium") -> dict:
    if settings.openai_api_key:
        try:
            return _openai_summary(text, length)
        except Exception:
            pass

    return _extractive_summary(text, length)