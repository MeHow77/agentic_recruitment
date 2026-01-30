from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMProvider(ABC):
    @abstractmethod
    async def generate_structured[T: BaseModel](self, prompt: str, output_model: type[T]) -> T:
        """Generate a structured response conforming to the given Pydantic model."""
        ...
