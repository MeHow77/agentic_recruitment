import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


def load_and_merge_data(personal_path: str, master_path: str) -> Dict[str, Any]:
    """
    Load two JSON files and merge them into a single dictionary.

    Args:
        personal_path: Path to personal_data.json
        master_path: Path to master_data.json
    """
    p_path = Path(personal_path)
    m_path = Path(master_path)

    if not p_path.exists() or not m_path.exists():
        raise FileNotFoundError("One or both data files are missing.")

    with open(p_path, "r", encoding="utf-8") as f:
        personal_data = json.load(f)

    with open(m_path, "r", encoding="utf-8") as f:
        master_data = json.load(f)

    merged_data = {**master_data, **personal_data}

    logger.info("Successfully merged data from %s and %s", personal_path, master_path)
    return merged_data


def render_markdown(template: str, data: Dict[str, Any], output: str) -> str:
    """
    Render Jinja2 template with a data dictionary.

    Args:
        template: Path to .j2 template file
        data: Dictionary containing the template variables
        output: Output markdown file path

    Returns:
        Path to the generated markdown file
    """
    template_path = Path(template)

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tpl = env.get_template(template_path.name)

    rendered = tpl.render(**data)

    output_path = Path(output)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    logger.info("Generated markdown: %s", output_path)
    return str(output_path)


def generate_pdf(
        input_md: str,
        output_pdf: str,
        cli_path: str,
        paper: str,
        font_size: int,
) -> str:
    """
    Generate PDF from markdown using md-resume CLI.
    """
    input_path = Path(input_md)
    if not input_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {input_path}")

    cli_bin = Path(cli_path)
    if not cli_bin.exists():
        raise FileNotFoundError(f"CLI not found: {cli_bin}")

    pdf_path = Path(output_pdf)

    cmd = [
        "node",
        str(cli_bin),
        str(input_path),
        "--output",
        str(pdf_path),
        "--paper",
        paper,
        "--font-size",
        str(font_size),
    ]

    logger.debug("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error("STDOUT: %s", result.stdout)
        logger.error("STDERR: %s", result.stderr)
        raise RuntimeError(f"PDF generation failed with code {result.returncode}")

    logger.info("Generated PDF: %s", pdf_path)
    return str(pdf_path)