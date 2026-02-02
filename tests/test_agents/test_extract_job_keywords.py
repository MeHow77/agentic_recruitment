from unittest.mock import AsyncMock

import pytest

from src.agents.extract_job_keywords import extract_job_keywords


async def test_prompt_formatting():
    mock_provider = AsyncMock()
    await extract_job_keywords("# Job: Engineer", mock_provider)

    prompt = mock_provider.generate_structured.call_args[0][0]
    assert "# Job: Engineer" in prompt


async def test_return_passthrough(sample_job_keywords):
    mock_provider = AsyncMock()
    mock_provider.generate_structured = AsyncMock(return_value=sample_job_keywords)

    result = await extract_job_keywords("some job", mock_provider)
    assert result is sample_job_keywords


async def test_prompt_contains_instructions():
    mock_provider = AsyncMock()
    await extract_job_keywords("test", mock_provider)

    prompt = mock_provider.generate_structured.call_args[0][0]
    assert "ATS" in prompt
    assert "keywords_for_ats" in prompt


async def test_exception_propagation():
    mock_provider = AsyncMock()
    mock_provider.generate_structured = AsyncMock(side_effect=RuntimeError("LLM down"))

    with pytest.raises(RuntimeError, match="LLM down"):
        await extract_job_keywords("job desc", mock_provider)
