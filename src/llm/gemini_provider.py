from google import genai
from pydantic import BaseModel

from src.llm.provider import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-3-flash-preview") -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    async def generate_structured[T: BaseModel](self, prompt: str, output_model: type[T]) -> T:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=output_model,
            ),
        )
        return output_model.model_validate_json(response.text)
