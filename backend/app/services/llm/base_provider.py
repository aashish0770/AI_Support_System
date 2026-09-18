# backend/app/services/llm/base_provider.py

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a single response given a system prompt and user message."""
