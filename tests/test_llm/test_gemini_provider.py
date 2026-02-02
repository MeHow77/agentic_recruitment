from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import BaseModel

from src.llm.gemini_provider import GeminiProvider


class SampleOutput(BaseModel):
    answer: str


@patch("src.llm.gemini_provider.genai")
async def test_structured_output_parsing(mock_genai):
    mock_response = MagicMock()
    mock_response.text = '{"answer": "42"}'
    mock_genai.Client.return_value.aio.models.generate_content = AsyncMock(
        return_value=mock_response
    )

    provider = GeminiProvider(api_key="fake")
    result = await provider.generate_structured("What?", SampleOutput)

    assert isinstance(result, SampleOutput)
    assert result.answer == "42"


@patch("src.llm.gemini_provider.genai")
async def test_config_passthrough(mock_genai):
    mock_response = MagicMock()
    mock_response.text = '{"answer": "ok"}'
    mock_generate = AsyncMock(return_value=mock_response)
    mock_genai.Client.return_value.aio.models.generate_content = mock_generate

    provider = GeminiProvider(api_key="fake")
    await provider.generate_structured("test prompt", SampleOutput)

    call_kwargs = mock_generate.call_args.kwargs
    assert call_kwargs["model"] == "gemini-3-flash-preview"
    assert call_kwargs["contents"] == "test prompt"
    mock_genai.types.GenerateContentConfig.assert_called_once()


@patch("src.llm.gemini_provider.genai")
async def test_custom_model_name(mock_genai):
    mock_response = MagicMock()
    mock_response.text = '{"answer": "ok"}'
    mock_generate = AsyncMock(return_value=mock_response)
    mock_genai.Client.return_value.aio.models.generate_content = mock_generate

    provider = GeminiProvider(api_key="fake", model="gemini-pro")
    await provider.generate_structured("test", SampleOutput)

    call_kwargs = mock_generate.call_args.kwargs
    assert call_kwargs["model"] == "gemini-pro"
