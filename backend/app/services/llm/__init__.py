# backend/app/services/llm/__init__.py

from functools import lru_cache

from app.services.llm.base_provider import LLMProvider
from app.services.llm.ollama_provider import OllamaProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Single place that dscides which provider is active. Swapping to a cloud
    provider later, means adding an OpenAIProvider, or a HuggingFaceProvider or any other LLMProvider.
    class and changing this one function, nothing else in the codebase should ever import OllamaProvideer directly.
    """
    return OllamaProvider()


__all__ = ["LLMProvider", "get_llm_provider"]