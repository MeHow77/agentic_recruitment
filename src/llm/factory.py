import logging

from src.llm.provider import LLMProvider
from src.llm.gemini_provider import GeminiProvider
from src.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


def create_llm_provider(
    *,
    llm_provider: str,
    llm_api_key: str | None,
    model: str | None = None,
) -> LLMProvider:
    model_kwargs = {"model": model} if model else {}
    match llm_provider:
        case "gemini":
            client = GeminiProvider(api_key=llm_api_key, **model_kwargs)
            logger.info("Using Gemini provider (model=%s)", client._model)
        case "openai":
            client = OpenAIProvider(api_key=llm_api_key, **model_kwargs)
            logger.info("Using OpenAI provider (model=%s)", client._model)
        case _:
            raise ValueError(f"Unknown LLM provider: {llm_provider}")
    return client