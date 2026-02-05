import json
import logging
from pathlib import Path

from pydantic import BaseModel

from src.storage.file_storage import FileStorage

logger = logging.getLogger(__name__)


class LocalFileFileStorage(FileStorage):
    def __init__(self, base_dir: Path = Path("outputs")) -> None:
        self._base_dir = base_dir

    def save_model(self, data: BaseModel | list[BaseModel], path: Path) -> Path:
        resolved = self._resolve_and_prepare(path)
        if isinstance(data, list):
            text = json.dumps(
                [item.model_dump(mode="json") for item in data],
                indent=2,
                ensure_ascii=False
            )
        else:
            text = data.model_dump_json(indent=2)
        resolved.write_text(text, encoding="utf-8")
        logger.info("Saved model data to %s", resolved)
        return resolved

    def _resolve_and_prepare(self, path: Path) -> Path:
        resolved = path if path.is_absolute() else self._base_dir / path
        resolved.parent.mkdir(parents=True, exist_ok=True)
        return resolved
