import asyncio
import json
import logging
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
from src.storage.local_file_storage import LocalFileFileStorage
from src.settings import Settings


def setup_logging(level="INFO"):
    """Configure logging with nice format."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


def _sanitize(name: str) -> str:
    """Sanitize a string for use in filenames."""
    return re.sub(r"[^\w\-]", "_", name).strip("_").lower()


def _build_output_dir(base: str | Path, company: str = "base", title: str = "resume") -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    return Path(base) / f"{timestamp}_{_sanitize(company)}_{_sanitize(title)}"


async def main():
    settings = Settings()
    logger = setup_logging(settings.log_level)

    logger.info("Starting resume generator")
    logger.info(f"Config - PORT: {settings.port}")
    logger.info(f"Config - MD_J2_TEMPLATE: {settings.md_j2_template}")
    logger.info(f"Config - MASTER_JSON: {settings.master_json}")
    logger.info(f"Config - PERSONAL_JSON: {settings.personal_json}")
    logger.info(f"Config - CLI_CONVERTER_PATH: {settings.cli_converter_path}")
    logger.info(f"Config - JOB_URLS_FILE: {settings.job_urls_file}")
    logger.info(f"Log level: {settings.log_level}")

    data_provider = JsonFileDataProvider()

    experience_data = data_provider.load_experience_data(settings.master_json)
    personal_data = data_provider.load_personal_data(settings.personal_json)

    if not settings.job_urls_file:
        logger.info("No job URLs file configured — generating base resume only")
        combined = {**experience_data.model_dump(), **personal_data}
        renderer = Jinja2TemplateRenderer(settings.md_j2_template)
        exporter = MarkdownToPDFExporter(
            renderer=renderer,
            cli_path=settings.cli_converter_path,
            paper=settings.pdf_paper_size,
            font_size=settings.pdf_font_size,
        )
        output_dir = _build_output_dir(settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        exporter.export(data=combined, output_path=output_dir / settings.pdf_filename)
        return

    job_urls = json.loads(settings.job_urls_file.read_text(encoding="utf-8"))
    if not job_urls:
        logger.info("Job URLs file is empty — skipping tailored generation")
        return

    provider = create_llm_provider(
        llm_provider=settings.llm_provider,
        llm_api_key=settings.llm_api_key.get_secret_value(),
        model=settings.llm_model,
    )

    renderer = Jinja2TemplateRenderer(settings.md_j2_template)
    exporter = MarkdownToPDFExporter(
        renderer=renderer,
        cli_path=settings.cli_converter_path,
        paper=settings.pdf_paper_size,
        font_size=settings.pdf_font_size,
    )

    for url in job_urls:
        logger.info("Processing job URL: %s", url)

        markdown_content = docling_url_to_markdown(url)
        logger.info("Extracted %d chars of markdown from %s", len(markdown_content), url)

        keywords = await extract_job_keywords(markdown_content, provider)

        output_dir = _build_output_dir(settings.output_dir, keywords.company_name, keywords.job_title)
        job_storage = LocalFileFileStorage(base_dir=output_dir)

        job_storage.save_model(
            JobKeywordResult(source_url=url, keywords=keywords),
            Path(settings.keywords_filename),
        )

        gaps = await analyze_skill_gaps(experience_data, keywords, provider)
        job_storage.save_model(gaps, Path(settings.gaps_filename))

        if settings.interactive:
            from src.agents.interactive_improvement import run_interactive_improvement
            from src.cli.console import QuestionaryConsole

            improved = await run_interactive_improvement(
                experience_data, gaps, provider, QuestionaryConsole()
            )
            adjusted = await adjust_data(improved, keywords, gaps, provider)
        else:
            adjusted = await adjust_data(experience_data, keywords, gaps, provider)

        combined = {**adjusted.model_dump(), **personal_data}
        exporter.export(data=combined, output_path=output_dir / settings.pdf_filename)

        logger.info("Generated tailored resume: %s", output_dir / settings.pdf_filename)


if __name__ == "__main__":
    asyncio.run(main())
