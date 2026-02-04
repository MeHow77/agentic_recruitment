import logging

from docling.document_converter import DocumentConverter

logger = logging.getLogger(__name__)

def docling_url_to_markdown(url: str) -> str:
    logger.info("Docling: Converting %s to markdown...", url)
    converter = DocumentConverter()
    result = converter.convert(url)
    return result.document.export_to_markdown()
