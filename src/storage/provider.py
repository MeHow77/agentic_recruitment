from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel


class StorageProvider(ABC):
    @abstractmethod
    def save_model(self, data: BaseModel | list[BaseModel], path: Path) -> Path:
        """Serialize a Pydantic model (or list of models) to persistent storage."""
        ...

    @abstractmethod
    def save_text(self, content: str, path: Path) -> Path:
        """Persist a plain text string. Returns the resolved path."""
        ...
