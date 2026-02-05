from pathlib import Path

import pytest

from src.settings import BASE_DIR, CONFIG_FILE, ENV_FILE, Settings


def _write_file(path: Path, content: str) -> str | None:
    original = path.read_text(encoding="utf-8") if path.exists() else None
    path.write_text(content, encoding="utf-8")
    return original


def _restore_file(path: Path, original: str | None) -> None:
    if original is None:
        if path.exists():
            path.unlink()
    else:
        path.write_text(original, encoding="utf-8")


def _base_config_text() -> str:
    return """
llm_provider = "openai"
md_j2_template = "templates/resume_template.md.j2"
master_json = "data/master_data.json"
personal_json = "data/personal_data.json"
cli_converter_path = "external/markdown_resume/packages/pdf-cli/bin/md-resume.js"
output_dir = "outputs"
pdf_paper_size = "A4"
pdf_font_size = 11
pdf_filename = "resume.pdf"
keywords_filename = "keywords.json"
gaps_filename = "gaps.json"
log_level = "INFO"
""".lstrip()


def test_loads_values_from_config_and_env(monkeypatch: pytest.MonkeyPatch) -> None:
    original_config = _write_file(CONFIG_FILE, _base_config_text())
    original_env = _write_file(ENV_FILE, "LLM_API_KEY=from-env\n")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    try:
        settings = Settings()
        assert settings.llm_provider == "openai"
        assert settings.pdf_font_size == 11
        assert settings.llm_api_key.get_secret_value() == "from-env"
    finally:
        _restore_file(CONFIG_FILE, original_config)
        _restore_file(ENV_FILE, original_env)


def test_cli_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    original_config = _write_file(CONFIG_FILE, _base_config_text())
    original_env = _write_file(ENV_FILE, "LLM_API_KEY=from-env\n")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    try:
        settings = Settings(llm_api_key="from-cli")
        assert settings.llm_api_key.get_secret_value() == "from-cli"
    finally:
        _restore_file(CONFIG_FILE, original_config)
        _restore_file(ENV_FILE, original_env)


def test_relative_paths_resolve_to_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    config_text = _base_config_text() + 'job_urls_file = "data/job_urls.json"\n'
    original_config = _write_file(CONFIG_FILE, config_text)
    original_env = _write_file(ENV_FILE, "LLM_API_KEY=from-env\n")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    try:
        settings = Settings()
        assert settings.md_j2_template == BASE_DIR / "templates/resume_template.md.j2"
        assert settings.master_json == BASE_DIR / "data/master_data.json"
        assert settings.personal_json == BASE_DIR / "data/personal_data.json"
        assert settings.cli_converter_path == (
            BASE_DIR / "external/markdown_resume/packages/pdf-cli/bin/md-resume.js"
        )
        assert settings.job_urls_file == BASE_DIR / "data/job_urls.json"
        assert settings.output_dir == BASE_DIR / "outputs"
    finally:
        _restore_file(CONFIG_FILE, original_config)
        _restore_file(ENV_FILE, original_env)


def test_missing_config_file_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    original_config = CONFIG_FILE.read_text(encoding="utf-8") if CONFIG_FILE.exists() else None
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
    original_env = _write_file(ENV_FILE, "LLM_API_KEY=from-env\n")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    try:
        with pytest.raises(FileNotFoundError, match="config.toml"):
            Settings()
    finally:
        _restore_file(CONFIG_FILE, original_config)
        _restore_file(ENV_FILE, original_env)
