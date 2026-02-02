import logging

from src.llm.provider import LLMProvider
from src.llm.gemini_provider import GeminiProvider
from src.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


def create_llm_provider(
    *,
    llm_provider: str,
    llm_api_key: str | None,
) -> LLMProvider:
    match llm_provider:
        case "gemini":
            client = GeminiProvider(api_key=llm_api_key)
            logger.info("Using Gemini provider")
        case "openai":
            client = OpenAIProvider(api_key=llm_api_key)
            logger.info("Using OpenAI provider")
        case _:
            raise ValueError(f"Unknown LLM provider: {llm_provider}")
    return client