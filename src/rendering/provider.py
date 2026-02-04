from abc import ABC, abstractmethod
from typing import Any, Dict


class TemplateRenderer(ABC):
    @abstractmethod
    def render(self, data: Dict[str, Any]) -> str:
        """Render data using a template and return the rendered content."""
        ...
