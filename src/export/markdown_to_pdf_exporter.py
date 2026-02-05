import logging
import subprocess
from pathlib import Path
from typing import Any, Dict

from src.export.document_exporter import DocumentExporter
from src.rendering.provider import TemplateRenderer

logger = logging.getLogger(__name__)


class MarkdownToPDFExporter(DocumentExporter):
    def __init__(
        self,
        renderer: TemplateRenderer,
        cli_path: Path,
        paper: str = "A4",
        font_size: int = 12,
    ) -> None:
        self._renderer = renderer
        self._cli_path = Path(cli_path)
        self._paper = paper
        self._font_size = font_size

    def export(self, data: Dict[str, Any], output_path: Path) -> Path:
        if not self._cli_path.exists():
            raise FileNotFoundError(f"CLI not found: {self._cli_path}")

        output_path = Path(output_path)
        md_path = output_path.with_suffix(".md")

        rendered = self._renderer.render(data)
        md_path.write_text(rendered, encoding="utf-8")
        logger.info("Generated markdown: %s", md_path)

        cmd = [
            "node",
            str(self._cli_path),
            str(md_path),
            "--output",
            str(output_path),
            "--paper",
            self._paper,
            "--font-size",
            str(self._font_size),
        ]

        logger.debug("Running: %s", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error("STDOUT: %s", result.stdout)
            logger.error("STDERR: %s", result.stderr)
            raise RuntimeError(
                f"PDF generation failed with code {result.returncode}"
            )

        logger.info("Generated PDF: %s", output_path)
        return output_path
