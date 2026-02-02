from abc import ABC, abstractmethod
from typing import Any, Dict


class DataProvider(ABC):
    @abstractmethod
    def load_data(self) -> Dict[str, Any]:
        """Load and return resume data as a dict ready for template rendering."""
        ...
