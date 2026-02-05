from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_FILE = BASE_DIR / "config.toml"
ENV_FILE = BASE_DIR / ".env"


def _resolve_path(path: Path | None) -> Path | None:
    if path is None:
        return None
    if path.is_absolute():
        return path
    return BASE_DIR / path


def _only_llm_api_key(
    source: Callable[[], dict[str, Any]],
) -> Callable[[], dict[str, Any]]:
    def _inner() -> dict[str, Any]:
        data = source()
        if "llm_api_key" in data:
            return {"llm_api_key": data["llm_api_key"]}
        if "LLM_API_KEY" in data:
            return {"llm_api_key": data["LLM_API_KEY"]}
        return {}

    return _inner


class StrictTomlConfigSettingsSource(TomlConfigSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings], toml_file: Path | None = CONFIG_FILE):
        if toml_file is None:
            raise FileNotFoundError("Missing config.toml at None")
        paths = toml_file if isinstance(toml_file, (list, tuple)) else [toml_file]
        if not any(Path(path).expanduser().is_file() for path in paths):
            raise FileNotFoundError(f"Missing config.toml at {toml_file}")
        super().__init__(settings_cls, toml_file=toml_file)

    def __call__(self) -> dict[str, Any]:
        data = super().__call__()
        data.pop("llm_api_key", None)
        return data


class Settings(BaseSettings):
    llm_api_key: SecretStr = Field(validation_alias="LLM_API_KEY")

    llm_provider: Literal["gemini", "openai"]
    md_j2_template: Path
    master_json: Path
    personal_json: Path
    cli_converter_path: Path
    job_urls_file: Path | None = None
    output_dir: Path = Path("outputs")
    llm_model: str | None = None
    pdf_paper_size: str = "A4"
    pdf_font_size: int = 12
    pdf_filename: str = "resume.pdf"
    keywords_filename: str = "keywords.json"
    gaps_filename: str = "gaps.json"
    log_level: str = "INFO"
    port: int | None = None
    interactive: bool = False

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
        case_sensitive=False,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: Callable[[], dict[str, Any]],
        env_settings: Callable[[], dict[str, Any]],
        dotenv_settings: Callable[[], dict[str, Any]],
        file_secret_settings: Callable[[], dict[str, Any]],
    ) -> tuple[Callable[[], dict[str, Any]], ...]:
        toml_settings = StrictTomlConfigSettingsSource(settings_cls, toml_file=CONFIG_FILE)
        return (
            init_settings,
            _only_llm_api_key(env_settings),
            _only_llm_api_key(dotenv_settings),
            toml_settings,
        )

    def model_post_init(self, __context: Any) -> None:
        self.md_j2_template = _resolve_path(self.md_j2_template)
        self.master_json = _resolve_path(self.master_json)
        self.personal_json = _resolve_path(self.personal_json)
        self.cli_converter_path = _resolve_path(self.cli_converter_path)
        self.job_urls_file = _resolve_path(self.job_urls_file)
        self.output_dir = _resolve_path(self.output_dir)
