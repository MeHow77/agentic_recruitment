from unittest.mock import MagicMock, patch

import pytest

from src.export.markdown_to_pdf_exporter import MarkdownToPDFExporter


@pytest.fixture
def mock_renderer():
    renderer = MagicMock()
    renderer.render.return_value = "# Resume Content"
    return renderer


@pytest.fixture
def cli_path(tmp_path):
    cli = tmp_path / "md-resume.js"
    cli.write_text("#!/usr/bin/env node")
    return cli


def test_happy_path(tmp_path, mock_renderer, cli_path):
    exporter = MarkdownToPDFExporter(renderer=mock_renderer, cli_path=cli_path)
    output = tmp_path / "resume.pdf"

    with patch("src.export.markdown_to_pdf_exporter.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = exporter.export({"name": "Jane"}, output)

    assert result == output
    mock_renderer.render.assert_called_once_with({"name": "Jane"})


def test_cli_args_verification(tmp_path, mock_renderer, cli_path):
    exporter = MarkdownToPDFExporter(renderer=mock_renderer, cli_path=cli_path)
    output = tmp_path / "resume.pdf"

    with patch("src.export.markdown_to_pdf_exporter.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        exporter.export({}, output)

    cmd = mock_run.call_args[0][0]
    assert cmd[0] == "node"
    assert str(cli_path) in cmd
    assert "--output" in cmd
    assert "--paper" in cmd
    assert "--font-size" in cmd


def test_custom_paper_and_font(tmp_path, mock_renderer, cli_path):
    exporter = MarkdownToPDFExporter(
        renderer=mock_renderer, cli_path=cli_path, paper="Letter", font_size=10
    )
    output = tmp_path / "resume.pdf"

    with patch("src.export.markdown_to_pdf_exporter.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        exporter.export({}, output)

    cmd = mock_run.call_args[0][0]
    paper_idx = cmd.index("--paper")
    font_idx = cmd.index("--font-size")
    assert cmd[paper_idx + 1] == "Letter"
    assert cmd[font_idx + 1] == "10"


def test_missing_cli_raises(tmp_path, mock_renderer):
    fake_cli = tmp_path / "nonexistent.js"
    exporter = MarkdownToPDFExporter(renderer=mock_renderer, cli_path=fake_cli)

    with pytest.raises(FileNotFoundError, match="CLI not found"):
        exporter.export({}, tmp_path / "out.pdf")


def test_nonzero_exit_raises(tmp_path, mock_renderer, cli_path):
    exporter = MarkdownToPDFExporter(renderer=mock_renderer, cli_path=cli_path)
    output = tmp_path / "resume.pdf"

    with patch("src.export.markdown_to_pdf_exporter.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        with pytest.raises(RuntimeError, match="PDF generation failed"):
            exporter.export({}, output)


def test_md_suffix(tmp_path, mock_renderer, cli_path):
    """Markdown intermediate file is written with .md suffix."""
    exporter = MarkdownToPDFExporter(renderer=mock_renderer, cli_path=cli_path)
    output = tmp_path / "resume.pdf"

    with patch("src.export.markdown_to_pdf_exporter.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        exporter.export({}, output)

    md_path = tmp_path / "resume.md"
    assert md_path.exists()
    assert md_path.read_text(encoding="utf-8") == "# Resume Content"


def test_renderer_delegation(tmp_path, mock_renderer, cli_path):
    exporter = MarkdownToPDFExporter(renderer=mock_renderer, cli_path=cli_path)
    data = {"a": 1, "b": [2, 3]}

    with patch("src.export.markdown_to_pdf_exporter.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        exporter.export(data, tmp_path / "out.pdf")

    mock_renderer.render.assert_called_once_with(data)


def test_string_path_coercion(tmp_path, mock_renderer, cli_path):
    exporter = MarkdownToPDFExporter(renderer=mock_renderer, cli_path=str(cli_path))
    output = tmp_path / "resume.pdf"

    with patch("src.export.markdown_to_pdf_exporter.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = exporter.export({}, str(output))

    assert result == output
