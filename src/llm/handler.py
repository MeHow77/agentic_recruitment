import logging

from pydantic import BaseModel

from src.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class LLMHandler:
    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    async def generate_structured[T: BaseModel](self, prompt: str, output_model: type[T]) -> T:
        logger.info("Generating structured output for model: %s", output_model.__name__)
        result = await self._provider.generate_structured(prompt, output_model)
        logger.info("Successfully generated %s", output_model.__name__)
        return result
