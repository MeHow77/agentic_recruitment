import logging

from src.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


def create_llm_provider(
    *,
    llm_provider: str,
    gemini_api_key: str | None,
    openai_api_key: str | None,
) -> LLMProvider:
    if llm_provider == "gemini":
        if not gemini_api_key:
            raise ValueError("--llm-provider is 'gemini' but no GEMINI_API_KEY provided")
        from src.llm.gemini_provider import GeminiProvider
        logger.info("Using Gemini provider")
        return GeminiProvider(api_key=gemini_api_key)

    if llm_provider == "openai":
        if not openai_api_key:
            raise ValueError("--llm-provider is 'openai' but no OPENAI_API_KEY provided")
        from src.llm.openai_provider import OpenAIProvider
        logger.info("Using OpenAI provider")
        return OpenAIProvider(api_key=openai_api_key)

    raise ValueError(f"Unknown LLM provider: '{llm_provider}'. Supported: 'gemini', 'openai'")
