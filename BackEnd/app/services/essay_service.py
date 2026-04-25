import re

from app.core.config import settings


def _normalize_text(text: str) -> str:
    text = text.replace("\r", " ").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _split_paragraphs(text: str) -> list[str]:
    text = _normalize_text(text)
    parts = [p.strip() for p in text.split("\n") if p.strip()]
    return parts


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _truncate(text: str, max_len: int = 240) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _fallback_feedback(text: str, level: str) -> dict:
    paragraphs = _split_paragraphs(text)
    sentences = _split_sentences(text)
    word_count = len(text.split())

    items = []

    if word_count < 80:
        items.append("Develop your ideas further with more explanation and supporting detail.")
    else:
        items.append("Your draft has enough material to build a clear argument, but some points can be made more specific.")

    if len(paragraphs) < 3:
        items.append("Try organizing the text into a clearer introduction, body, and conclusion.")
    else:
        items.append("The paragraph structure is present, but transitions between ideas can be smoother.")

    if len(sentences) > 0:
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_sentence_length > 25:
            items.append("Some sentences are quite long; shorter sentences would improve clarity.")
        else:
            items.append("Sentence length is generally readable, though some sentences could be more precise.")

    if "because" not in text.lower() and "because" not in text.lower() and "поэтому" not in text.lower():
        items.append("Strengthen your reasoning by making cause-and-effect links more explicit.")

    main_text = (
        f"This {level}-level draft shows a workable starting point, but it would benefit from clearer structure, "
        f"more specific argument development, and stronger links between ideas."
    )

    return {
        "title": "Essay Feedback",
        "main_text": main_text,
        "items": items[:5],
    }


def _fallback_outline(text: str, level: str) -> dict:
    topic = _truncate(text, 120)

    return {
        "title": "Essay Outline",
        "main_text": f"Here is a simple {level}-level outline for the topic: {topic}",
        "items": [
            "Introduction: present the topic, provide context, and state the main thesis.",
            "Body paragraph 1: explain the first main point with examples or evidence.",
            "Body paragraph 2: develop the second main point and connect it to the thesis.",
            "Body paragraph 3: address another perspective, implication, or counterargument.",
            "Conclusion: restate the thesis and summarize the key takeaway."
        ],
    }


def _fallback_brainstorm(text: str, level: str) -> dict:
    topic = _truncate(text, 120)

    return {
        "title": "Brainstorm Ideas",
        "main_text": f"Here are several directions you can explore for this {level}-level writing topic: {topic}",
        "items": [
            "Define the core problem or question behind the topic.",
            "Identify the main causes, effects, or consequences.",
            "Consider different viewpoints or stakeholders involved.",
            "Use a real-world example, case, or comparison.",
            "End with a broader implication, solution, or lesson."
        ],
    }


def _fallback_improve(text: str, level: str) -> dict:
    cleaned = _normalize_text(text)
    sentences = _split_sentences(cleaned)

    if not sentences:
        improved = cleaned
    else:
        improved = " ".join(sentences[:5])

    return {
        "title": "Improved Writing",
        "main_text": _truncate(
            f"This revised version keeps your original meaning but aims for clearer flow and more polished phrasing: {improved}",
            700,
        ),
        "items": [
            "Clarified wording to make the main point easier to follow.",
            "Reduced repetition where possible.",
            "Improved flow between ideas.",
        ],
    }


def _openai_essay(text: str, mode: str, level: str) -> dict:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)

    mode_instructions = {
        "feedback": (
            "Give constructive writing feedback. Focus on structure, clarity, argument, evidence, and style. "
            "Be specific and helpful, not harsh."
        ),
        "outline": (
            "Generate a clear essay outline. Include a thesis direction, introduction, body flow, and conclusion."
        ),
        "brainstorm": (
            "Generate strong brainstorming ideas, angles, arguments, and directions the user can explore."
        ),
        "improve": (
            "Rewrite the user's text to improve clarity, flow, grammar, and style while preserving the original meaning."
        ),
    }

    instruction = mode_instructions.get(mode, mode_instructions["feedback"])

    system_prompt = (
        "You are an academic writing assistant. "
        "Provide practical and structured help for essays and short academic writing. "
        "Adapt the answer for the user's stated level. "
        "Return output in exactly this format:\n\n"
        "TITLE:\n"
        "<short title>\n\n"
        "MAIN_TEXT:\n"
        "<main paragraph>\n\n"
        "ITEMS:\n"
        "- <item 1>\n"
        "- <item 2>\n"
        "- <item 3>\n"
    )

    user_prompt = f"""
Mode: {mode}
Level: {level}

Task:
{instruction}

User text:
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

    title = "Essay Helper Result"
    main_text = ""
    items = []

    title_match = re.search(r"TITLE:\s*(.+?)(?:\n|$)", output, re.DOTALL)
    main_match = re.search(r"MAIN_TEXT:\s*(.+?)(?:\nITEMS:|$)", output, re.DOTALL)
    items_match = re.search(r"ITEMS:\s*(.+)$", output, re.DOTALL)

    if title_match:
        title = title_match.group(1).strip()

    if main_match:
        main_text = main_match.group(1).strip()

    if items_match:
        for line in items_match.group(1).splitlines():
            cleaned = line.strip()
            if cleaned.startswith("-"):
                item = cleaned.lstrip("-").strip()
                if item:
                    items.append(item)

    if not main_text:
        lines = [line.strip() for line in output.splitlines() if line.strip()]
        if lines:
            title = lines[0]
        if len(lines) > 1:
            main_text = lines[1]
        if len(lines) > 2:
            items = lines[2:7]

    return {
        "title": title,
        "main_text": main_text or "Could not generate a response.",
        "items": items[:5],
    }


def process_essay_request(text: str, mode: str, level: str = "college") -> dict:
    if settings.openai_api_key:
        try:
            return _openai_essay(text=text, mode=mode, level=level)
        except Exception:
            pass

    if mode == "feedback":
        return _fallback_feedback(text, level)
    if mode == "outline":
        return _fallback_outline(text, level)
    if mode == "brainstorm":
        return _fallback_brainstorm(text, level)
    if mode == "improve":
        return _fallback_improve(text, level)

    raise ValueError(f"Unsupported essay mode: {mode}")