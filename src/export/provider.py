from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class DocumentExporter(ABC):
    @abstractmethod
    def export(self, data: Dict[str, Any], output_path: Path) -> Path:
        """Export data to a document at output_path."""
        ...
