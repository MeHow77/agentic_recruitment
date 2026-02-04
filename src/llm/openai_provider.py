from openai import AsyncOpenAI
from pydantic import BaseModel

from src.llm.provider import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-2024-08-06") -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate_structured[T: BaseModel](self, prompt: str, output_model: type[T]) -> T:
        response = await self._client.responses.parse(
            model=self._model,
            input=[{"role": "user", "content": prompt}],
            text_format=output_model,
        )
        result = response.output_parsed
        if result is None:
            raise ValueError(
                f"OpenAI returned a refusal or empty parsed result for {output_model.__name__}"
            )
        return result
