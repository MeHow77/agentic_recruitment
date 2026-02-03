from abc import ABC, abstractmethod
from typing import Any, Dict
from pathlib import Path


class DataProvider(ABC):

    @classmethod
    @abstractmethod
    def load_data(cls, personal_data: Path, master_data: Path) -> Dict[str, Any]:
        """Load and return resume data as a dict ready for template rendering."""
        ...
