import json
import logging
from typing import Any, Dict
from pathlib import Path

from src.data.provider import DataProvider
from src.models.experience_data import ExperienceData

logger = logging.getLogger(__name__)


class JsonFileDataProvider(DataProvider):

    @classmethod
    def load_data(cls, personal_path: Path, master_path: Path) -> Dict[str, Any]:
        if not personal_path.exists() or not master_path.exists():
            raise FileNotFoundError("One or both data files are missing.")

        with open(personal_path, "r", encoding="utf-8") as f:
            personal_data = json.load(f)

        with open(master_path, "r", encoding="utf-8") as f:
            master_data = json.load(f)

        merged_data = {**master_data, **personal_data}

        logger.info(
            "Successfully merged data from %s and %s",
            personal_path,
            master_path,
        )
        return merged_data

    @classmethod
    def load_experience_data(cls, path: Path) -> ExperienceData:
        if not path.exists():
            raise FileNotFoundError(f"Master data file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        logger.info("Loaded experience data from %s", path)
        return ExperienceData.model_validate(raw)

    @classmethod
    def load_personal_data(cls, path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Personal data file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info("Loaded personal data from %s", path)
        return data
