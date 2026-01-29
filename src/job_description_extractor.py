import logging

from docling.document_converter import DocumentConverter


def docling_url_to_markdown(url: str) -> str:
    logging.info(f"[*] Docling: Converting {url} to markdown...")
    converter = DocumentConverter()
    result = converter.convert(url)
    return result.document.export_to_markdown()

