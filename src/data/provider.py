from abc import ABC, abstractmethod
from typing import Any, Dict
from pathlib import Path

from src.models.experience_data import ExperienceData


class DataProvider(ABC):

    @classmethod
    @abstractmethod
    def load_data(cls, personal_data: Path, master_data: Path) -> Dict[str, Any]:
        """Load and return resume data as a dict ready for template rendering."""
        ...

    @classmethod
    @abstractmethod
    def load_experience_data(cls, path: Path) -> ExperienceData:
        """Load master resume data as a typed ExperienceData model."""
        ...

    @classmethod
    @abstractmethod
    def load_personal_data(cls, path: Path) -> Dict[str, Any]:
        """Load personal data as a raw dict."""
        ...
