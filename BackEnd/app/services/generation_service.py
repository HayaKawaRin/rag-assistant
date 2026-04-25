from app.core.config import settings


def build_structured_extractive_answer(question: str, context: str) -> str:
    if not context.strip():
        return "I could not find enough relevant information in the uploaded documents."

    paragraphs = [p.strip() for p in context.split("\n\n") if p.strip()]
    if not paragraphs:
        return "I could not assemble a clean answer from the retrieved context."

    summary = paragraphs[0]

    key_points = paragraphs[1:4]
    bullet_lines = "\n".join(f"- {point}" for point in key_points if point)

    answer_parts = [
        f"**Answer:** {summary}"
    ]

    if bullet_lines:
        answer_parts.append("**Key points:**")
        answer_parts.append(bullet_lines)

    return "\n\n".join(answer_parts).strip()


def build_openai_answer(question: str, context: str) -> str:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set.")

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)

    system_prompt = (
        "You are a helpful RAG assistant. "
        "Answer ONLY using the provided context. "
        "If the context is insufficient, say so clearly. "
        "Structure the answer with:\n"
        "1. A short direct answer.\n"
        "2. 3-5 bullet points with key facts.\n"
        "3. If useful, one short example.\n"
        "Do not invent facts outside the context."
    )

    user_prompt = f"""Question:
{question}

Context:
{context}
"""

    response = client.responses.create(
        model=settings.openai_chat_model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.output_text.strip()


def generate_answer(question: str, context: str) -> str:
    provider = settings.generation_provider.lower()

    if provider == "extractive":
        return build_structured_extractive_answer(question, context)

    if provider == "openai":
        return build_openai_answer(question, context)

    raise ValueError(f"Unsupported generation provider: {settings.generation_provider}")