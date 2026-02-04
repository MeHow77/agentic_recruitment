import argparse
import asyncio
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path

from src.agents.extract_job_keywords import extract_job_keywords
from src.agents.analyze_skill_gaps import analyze_skill_gaps
from src.agents.adjust_data import adjust_data
from src.job_description_data_extraction import docling_url_to_markdown
from src.data.json_file_provider import JsonFileDataProvider
from src.rendering.jinja_renderer import Jinja2TemplateRenderer
from src.export.markdown_to_pdf_exporter import MarkdownToPDFExporter
from src.models.extraction_run import JobKeywordResult
from src.llm.factory import create_llm_provider
from src.storage.local_file_storage import LocalFileStorage


def setup_logging(level="INFO"):
    """Configure logging with nice format."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Resume generator")

    parser.add_argument("--port", type=int, default=os.getenv("PORT"))
    parser.add_argument("--llm_api_key", type=str, default=os.getenv("LLM_API_KEY"))
    parser.add_argument("--llm_provider", type=str, default=os.getenv("LLM_PROVIDER"), choices=["gemini", "openai"])
    parser.add_argument("--md_j2_template", default=os.getenv("MD_J2_TEMPLATE"))
    parser.add_argument("--master_json", default=os.getenv("MASTER_JSON"))
    parser.add_argument("--personal_json", default=os.getenv("PERSONAL_JSON"))
    parser.add_argument("--cli_converter_path", default=os.getenv("CLI_CONVERTER_PATH"))
    parser.add_argument("--job_urls_file", default=os.getenv("JOB_URLS_FILE"))
    parser.add_argument("--output_dir", default=os.getenv("OUTPUT_DIR", "outputs"))
    parser.add_argument("--llm_model", default=os.getenv("LLM_MODEL"))
    parser.add_argument("--pdf_paper_size", default=os.getenv("PDF_PAPER_SIZE", "A4"))
    parser.add_argument("--pdf_font_size", type=int, default=int(os.getenv("PDF_FONT_SIZE", "12")))
    parser.add_argument("--pdf_filename", default=os.getenv("PDF_FILENAME", "resume.pdf"))
    parser.add_argument("--keywords_filename", default=os.getenv("KEYWORDS_FILENAME", "keywords.json"))
    parser.add_argument("--gaps_filename", default=os.getenv("GAPS_FILENAME", "gaps.json"))

    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))

    args = parser.parse_args()
    args.md_j2_template = Path(args.md_j2_template)
    args.master_json = Path(args.master_json)
    args.personal_json = Path(args.personal_json)
    args.cli_converter_path = Path(args.cli_converter_path)
    if args.job_urls_file:
        args.job_urls_file = Path(args.job_urls_file)
    return args


def _sanitize(name: str) -> str:
    """Sanitize a string for use in filenames."""
    return re.sub(r"[^\w\-]", "_", name).strip("_").lower()


def _build_output_dir(base: str, company: str = "base", title: str = "resume") -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return Path(base) / f"{timestamp}_{_sanitize(company)}_{_sanitize(title)}"


async def main():
    args = parse_args()
    logger = setup_logging(args.log_level)

    logger.info("Starting resume generator")
    logger.info(f"Config - PORT: {args.port}")
    logger.info(f"Config - MD_J2_TEMPLATE: {args.md_j2_template}")
    logger.info(f"Config - MASTER_JSON: {args.master_json}")
    logger.info(f"Config - PERSONAL_JSON: {args.personal_json}")
    logger.info(f"Config - CLI_CONVERTER_PATH: {args.cli_converter_path}")
    logger.info(f"Config - JOB_URLS_FILE: {args.job_urls_file}")
    logger.info(f"Log level: {args.log_level}")

    data_provider = JsonFileDataProvider()

    experience_data = data_provider.load_experience_data(args.master_json)
    personal_data = data_provider.load_personal_data(args.personal_json)

    if not args.job_urls_file:
        logger.info("No job URLs file configured — generating base resume only")
        combined = {**experience_data.model_dump(), **personal_data}
        renderer = Jinja2TemplateRenderer(args.md_j2_template)
        exporter = MarkdownToPDFExporter(
            renderer=renderer,
            cli_path=args.cli_converter_path,
            paper=args.pdf_paper_size,
            font_size=args.pdf_font_size,
        )
        output_dir = _build_output_dir(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        exporter.export(data=combined, output_path=output_dir / args.pdf_filename)
        return

    job_urls = json.loads(args.job_urls_file.read_text(encoding="utf-8"))
    if not job_urls:
        logger.info("Job URLs file is empty — skipping tailored generation")
        return

    provider = create_llm_provider(
        llm_provider=args.llm_provider,
        llm_api_key=args.llm_api_key,
        model=args.llm_model,
    )

    renderer = Jinja2TemplateRenderer(args.md_j2_template)
    exporter = MarkdownToPDFExporter(
        renderer=renderer,
        cli_path=args.cli_converter_path,
        paper=args.pdf_paper_size,
        font_size=args.pdf_font_size,
    )

    for url in job_urls:
        logger.info("Processing job URL: %s", url)

        markdown_content = docling_url_to_markdown(url)
        logger.info("Extracted %d chars of markdown from %s", len(markdown_content), url)

        keywords = await extract_job_keywords(markdown_content, provider)

        output_dir = _build_output_dir(args.output_dir, keywords.company_name, keywords.job_title)
        job_storage = LocalFileStorage(base_dir=output_dir)

        job_storage.save_model(
            JobKeywordResult(source_url=url, keywords=keywords),
            Path(args.keywords_filename),
        )

        gaps = await analyze_skill_gaps(experience_data, keywords, provider)
        job_storage.save_model(gaps, Path(args.gaps_filename))

        adjusted = await adjust_data(experience_data, keywords, gaps, provider)

        combined = {**adjusted.model_dump(), **personal_data}
        exporter.export(data=combined, output_path=output_dir / args.pdf_filename)

        logger.info("Generated tailored resume: %s", output_dir / args.pdf_filename)


if __name__ == "__main__":
    asyncio.run(main())
