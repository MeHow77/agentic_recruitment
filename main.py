import argparse
import asyncio
import logging
import os
from pathlib import Path

from src.agents.extract_job_keywords import extract_job_keywords
from src.job_description_data_extraction import docling_url_to_markdown
from src.data.json_file_provider import JsonFileDataProvider
from src.rendering.jinja_renderer import Jinja2TemplateRenderer
from src.export.markdown_to_pdf_exporter import MarkdownToPDFExporter
from src.models.extraction_run import JobKeywordResult
from src.llm.factory import create_llm_provider
from src.storage.local_file_storage import LocalFileStorage

JOB_URLS: list[str] = [
     "https://justjoin.it/job-offer/nike-senior-software-engineer-gdansk-ai",
]


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

    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))

    args = parser.parse_args()
    args.md_j2_template = Path(args.md_j2_template)
    args.master_json = Path(args.master_json)
    args.personal_json = Path(args.personal_json)
    args.cli_converter_path = Path(args.cli_converter_path)
    args.llm_provider = args.llm_provider
    return args


async def main():
    args = parse_args()
    logger = setup_logging(args.log_level)

    logger.info("Starting resume generator")
    logger.info(f"Config - PORT: {args.port}")
    logger.info(f"Config - MD_J2_TEMPLATE: {args.md_j2_template}")
    logger.info(f"Config - MASTER_JSON: {args.master_json}")
    logger.info(f"Config - PERSONAL_JSON: {args.personal_json}")
    logger.info(f"Config - CLI_CONVERTER_PATH: {args.cli_converter_path}")
    logger.info(f"Log level: {args.log_level}")

    storage = LocalFileStorage()

    if not JOB_URLS:
        logger.info("No job URLs configured — skipping keyword extraction")
        return
    provider = create_llm_provider(
        llm_provider=args.llm_provider,
        llm_api_key=args.llm_api_key,
    )

    results: list[JobKeywordResult] = []
    for url in JOB_URLS:
        logger.info("Extracting keywords from: %s", url)
        markdown_content = docling_url_to_markdown(url)
        logger.info("Extracted %d chars of markdown from %s", len(markdown_content), url)
        keywords = await extract_job_keywords(markdown_content, provider)
        results.append(JobKeywordResult(source_url=url, keywords=keywords))

    if not results:
        logger.info(f"No keywords extracted from {JOB_URLS}")
        return

    logger.info(f"Saving extracted keywords from {JOB_URLS}")
    storage.save_model(results, Path("extraction_run.json"))

    data_provider = JsonFileDataProvider()
    renderer = Jinja2TemplateRenderer(args.md_j2_template)
    exporter = MarkdownToPDFExporter(renderer=renderer, cli_path=args.cli_converter_path)

    logger.info("Merging data from personal_data.json and master_data.json")
    combined_data = data_provider.load_data(args.personal_json, args.master_json)

    logger.info("Generating resume PDF")
    exporter.export(data=combined_data, output_path=Path("outputs/resume.pdf"))


if __name__ == "__main__":
    asyncio.run(main())