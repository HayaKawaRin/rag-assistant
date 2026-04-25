from openai import OpenAI

from app.core.config import settings
from app.providers.llm.base import LLMProvider


class OpenAILLMProvider(LLMProvider):
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=getattr(settings, "openai_base_url", None) or None,
        )

        self.model = (
            getattr(settings, "chat_model", None)
            or getattr(settings, "openai_model", None)
            or getattr(settings, "model_name", None)
            or "gpt-4o-mini"
        )

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Answer only from the provided context. If the context is insufficient, say so clearly.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()


llm_provider = OpenAILLMProvider()