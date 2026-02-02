from unittest.mock import MagicMock, patch

import pytest

from src.job_description_data_extraction import docling_url_to_markdown


@patch("src.job_description_data_extraction.DocumentConverter")
def test_returns_markdown(mock_converter_cls):
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "# Job Title\nDescription"
    mock_converter_cls.return_value.convert.return_value = mock_result

    md = docling_url_to_markdown("https://example.com/job")
    assert md == "# Job Title\nDescription"


@patch("src.job_description_data_extraction.DocumentConverter")
def test_url_passthrough(mock_converter_cls):
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = ""
    mock_converter_cls.return_value.convert.return_value = mock_result

    docling_url_to_markdown("https://specific-url.com/posting")
    mock_converter_cls.return_value.convert.assert_called_once_with(
        "https://specific-url.com/posting"
    )


@patch("src.job_description_data_extraction.DocumentConverter")
def test_exception_propagation(mock_converter_cls):
    mock_converter_cls.return_value.convert.side_effect = RuntimeError("Network error")

    with pytest.raises(RuntimeError, match="Network error"):
        docling_url_to_markdown("https://example.com")
