from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from src.llm.openai_provider import OpenAIProvider


class SampleOutput(BaseModel):
    answer: str


@patch("src.llm.openai_provider.AsyncOpenAI")
async def test_structured_output_parsing(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_response.output_parsed = SampleOutput(answer="42")
    mock_client.responses.parse = AsyncMock(return_value=mock_response)

    provider = OpenAIProvider(api_key="fake")
    result = await provider.generate_structured("What?", SampleOutput)

    assert isinstance(result, SampleOutput)
    assert result.answer == "42"


@patch("src.llm.openai_provider.AsyncOpenAI")
async def test_refusal_raises_value_error(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_response.output_parsed = None
    mock_client.responses.parse = AsyncMock(return_value=mock_response)

    provider = OpenAIProvider(api_key="fake")
    with pytest.raises(ValueError, match="refusal or empty"):
        await provider.generate_structured("What?", SampleOutput)


@patch("src.llm.openai_provider.AsyncOpenAI")
async def test_custom_model_name(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_response.output_parsed = SampleOutput(answer="ok")
    mock_client.responses.parse = AsyncMock(return_value=mock_response)

    provider = OpenAIProvider(api_key="fake", model="gpt-4-turbo")
    await provider.generate_structured("test", SampleOutput)

    call_kwargs = mock_client.responses.parse.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4-turbo"
