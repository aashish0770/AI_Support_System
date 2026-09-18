# backend/app/services/llm/ollama_provider.py

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from app.core.config import get_settings
from app.services.llm.base_provider import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self._llm = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.2,
        )

    def generate(self, system_prompt: str, user_message: str) -> str:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]
        response = self._llm.invoke(messages)
        return response.content
