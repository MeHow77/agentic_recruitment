import json
import logging
from pathlib import Path
from typing import Any, Dict

from src.data.provider import DataProvider

logger = logging.getLogger(__name__)


class JsonFileDataProvider(DataProvider):
    def __init__(self, personal_path: Path, master_path: Path) -> None:
        self._personal_path = Path(personal_path)
        self._master_path = Path(master_path)

    def load_data(self) -> Dict[str, Any]:
        if not self._personal_path.exists() or not self._master_path.exists():
            raise FileNotFoundError("One or both data files are missing.")

        with open(self._personal_path, "r", encoding="utf-8") as f:
            personal_data = json.load(f)

        with open(self._master_path, "r", encoding="utf-8") as f:
            master_data = json.load(f)

        merged_data = {**master_data, **personal_data}

        logger.info(
            "Successfully merged data from %s and %s",
            self._personal_path,
            self._master_path,
        )
        return merged_data
