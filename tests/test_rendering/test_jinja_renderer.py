from pathlib import Path

import pytest

from src.rendering.jinja_renderer import Jinja2TemplateRenderer


def test_simple_render(tmp_path, minimal_template_content):
    template = tmp_path / "tpl.md.j2"
    template.write_text(minimal_template_content)

    renderer = Jinja2TemplateRenderer(template)
    result = renderer.render({"name": "World"})
    assert result == "Hello World!"


def test_loop_rendering(tmp_path, resume_template_content):
    template = tmp_path / "resume.md.j2"
    template.write_text(resume_template_content)

    data = {
        "personal": {"name": "Jane Doe"},
        "experience": [
            {"title": "Dev", "company": "Acme", "bullets": ["Built APIs"]},
        ],
    }
    renderer = Jinja2TemplateRenderer(template)
    result = renderer.render(data)
    assert "Jane Doe" in result
    assert "Dev at Acme" in result
    assert "Built APIs" in result


def test_file_not_found():
    renderer = Jinja2TemplateRenderer(Path("/nonexistent/template.j2"))
    with pytest.raises(FileNotFoundError):
        renderer.render({})


def test_trim_blocks(tmp_path):
    """trim_blocks removes first newline after a block tag."""
    template = tmp_path / "trim.j2"
    template.write_text("{% if true %}\nhello\n{% endif %}")

    renderer = Jinja2TemplateRenderer(template)
    result = renderer.render({})
    assert result == "hello\n"


def test_lstrip_blocks(tmp_path):
    """lstrip_blocks strips leading whitespace before block tags."""
    template = tmp_path / "lstrip.j2"
    template.write_text("  {% if true %}\nhello\n  {% endif %}")

    renderer = Jinja2TemplateRenderer(template)
    result = renderer.render({})
    assert result == "hello\n"


def test_top_level_kwargs(tmp_path):
    """Data keys are passed as top-level template variables via **data."""
    template = tmp_path / "vars.j2"
    template.write_text("{{ greeting }} {{ target }}")

    renderer = Jinja2TemplateRenderer(template)
    result = renderer.render({"greeting": "Hi", "target": "there"})
    assert result == "Hi there"


def test_string_path_coercion(tmp_path, minimal_template_content):
    template = tmp_path / "string.j2"
    template.write_text(minimal_template_content)

    renderer = Jinja2TemplateRenderer(str(template))
    result = renderer.render({"name": "Test"})
    assert result == "Hello Test!"


def test_nested_data(tmp_path):
    template = tmp_path / "nested.j2"
    template.write_text("{{ a.b.c }}")

    renderer = Jinja2TemplateRenderer(template)
    result = renderer.render({"a": {"b": {"c": "deep"}}})
    assert result == "deep"
