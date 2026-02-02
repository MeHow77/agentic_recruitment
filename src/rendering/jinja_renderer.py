import logging
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from src.rendering.provider import TemplateRenderer

logger = logging.getLogger(__name__)


class Jinja2TemplateRenderer(TemplateRenderer):
    def __init__(self, template_path: Path) -> None:
        self._template_path = Path(template_path)

    def render(self, data: Dict[str, Any]) -> str:
        if not self._template_path.exists():
            raise FileNotFoundError(f"Template not found: {self._template_path}")

        env = Environment(
            loader=FileSystemLoader(self._template_path.parent),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        tpl = env.get_template(self._template_path.name)

        return tpl.render(**data)
