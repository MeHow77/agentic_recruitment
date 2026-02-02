import pytest
from pydantic import ValidationError

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


def test_construction_with_all_fields(sample_job_keywords):
    assert sample_job_keywords.job_title == "Senior Backend Engineer"
    assert sample_job_keywords.company_name == "Acme Corp"
    assert sample_job_keywords.seniority_level == "Senior"


def test_list_fields_are_lists(sample_job_keywords):
    assert isinstance(sample_job_keywords.required_technical_skills, list)
    assert isinstance(sample_job_keywords.preferred_technical_skills, list)
    assert isinstance(sample_job_keywords.required_soft_skills, list)
    assert isinstance(sample_job_keywords.preferred_certifications, list)
    assert isinstance(sample_job_keywords.key_responsibilities, list)
    assert isinstance(sample_job_keywords.keywords_for_ats, list)


def test_keywords_for_ats_max_length_constraint():
    """keywords_for_ats has max_length=20."""
    too_many = [f"kw{i}" for i in range(21)]
    with pytest.raises(ValidationError):
        _make_keywords(keywords_for_ats=too_many)


def test_json_roundtrip(sample_job_keywords):
    json_str = sample_job_keywords.model_dump_json()
    restored = JobDescriptionKeywords.model_validate_json(json_str)
    assert restored == sample_job_keywords


def test_empty_lists_are_valid():
    kw = _make_keywords()
    assert kw.required_technical_skills == []
    assert kw.keywords_for_ats == []
