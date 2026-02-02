from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.models.extraction_run import JobKeywordResult
from src.models.job_keywords import JobDescriptionKeywords


def _make_keywords(**overrides):
    defaults = dict(
        job_title="Engineer",
        seniority_level="Mid",
        years_of_experience="3",
        company_name="Co",
        department_or_team="",
        required_technical_skills=[],
        preferred_technical_skills=[],
        required_soft_skills=[],
        required_education="",
        preferred_certifications=[],
        key_responsibilities=[],
        industry_domain="",
        keywords_for_ats=[],
        summary_of_role="A role.",
    )
    defaults.update(overrides)
    return JobDescriptionKeywords(**defaults)


def test_auto_uuid():
    result = JobKeywordResult(source_url="https://example.com", keywords=_make_keywords())
    assert result.run_id
    assert len(result.run_id) == 36  # UUID format: 8-4-4-4-12


def test_auto_utc_timestamp():
    before = datetime.now(tz=timezone.utc)
    result = JobKeywordResult(source_url="https://example.com", keywords=_make_keywords())
    after = datetime.now(tz=timezone.utc)
    assert before <= result.timestamp <= after
    assert result.timestamp.tzinfo is not None


def test_unique_ids():
    a = JobKeywordResult(source_url="https://a.com", keywords=_make_keywords())
    b = JobKeywordResult(source_url="https://b.com", keywords=_make_keywords())
    assert a.run_id != b.run_id


def test_serialization_roundtrip():
    original = JobKeywordResult(source_url="https://example.com", keywords=_make_keywords())
    json_str = original.model_dump_json()
    restored = JobKeywordResult.model_validate_json(json_str)
    assert restored.run_id == original.run_id
    assert restored.source_url == original.source_url
    assert restored.keywords == original.keywords


def test_source_url_is_required():
    with pytest.raises(ValidationError):
        JobKeywordResult(keywords=_make_keywords())


def test_keywords_field_is_required():
    with pytest.raises(ValidationError):
        JobKeywordResult(source_url="https://example.com")
