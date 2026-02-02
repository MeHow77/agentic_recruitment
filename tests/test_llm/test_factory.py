from unittest.mock import patch

import pytest

from src.llm.factory import create_llm_provider


@patch("src.llm.factory.GeminiProvider")
def test_gemini_dispatch(mock_cls):
    provider = create_llm_provider(llm_provider="gemini", llm_api_key="key123")
    mock_cls.assert_called_once_with(api_key="key123")
    assert provider is mock_cls.return_value


@patch("src.llm.factory.OpenAIProvider")
def test_openai_dispatch(mock_cls):
    provider = create_llm_provider(llm_provider="openai", llm_api_key="key456")
    mock_cls.assert_called_once_with(api_key="key456")
    assert provider is mock_cls.return_value


def test_unknown_provider_raises():
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        create_llm_provider(llm_provider="anthropic", llm_api_key="key")


def test_keyword_only_args():
    """create_llm_provider requires keyword-only arguments (leading *)."""
    with pytest.raises(TypeError):
        create_llm_provider("gemini", "key")
