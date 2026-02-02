import pytest
from pydantic import BaseModel

from src.models.job_keywords import JobDescriptionKeywords


class DummyModel(BaseModel):
    name: str
    value: int


@pytest.fixture
def sample_personal_data():
    return {
        "personal": {
            "name": "Jane Doe",
            "github": "janedoe",
            "phone": "+1-555-0100",
            "address": "New York, NY",
            "linkedin": "linkedin.com/in/janedoe",
            "email": "jane@example.com",
        }
    }


@pytest.fixture
def sample_master_data():
    return {
        "summary": "Experienced software engineer",
        "experience": [
            {
                "title": "Senior Developer",
                "company": "Acme Corp",
                "date": "2020-2024",
                "bullets": ["Led team of 5", "Built microservices"],
            }
        ],
        "education": [
            {
                "degree": "BSc Computer Science",
                "date": "2016-2020",
                "school": "MIT",
                "location": "Cambridge, MA",
            }
        ],
        "skills": {
            "languages": "Python, JavaScript",
            "tools": "Docker, K8s",
            "spoken": "English, Spanish",
        },
    }


@pytest.fixture
def sample_merged_data(sample_personal_data, sample_master_data):
    return {**sample_master_data, **sample_personal_data}


@pytest.fixture
def sample_job_keywords():
    return JobDescriptionKeywords(
        job_title="Senior Backend Engineer",
        seniority_level="Senior",
        years_of_experience="5+",
        company_name="Acme Corp",
        department_or_team="Platform",
        required_technical_skills=["Python", "PostgreSQL"],
        preferred_technical_skills=["Go"],
        required_soft_skills=["Communication"],
        required_education="Bachelor's in CS",
        preferred_certifications=["AWS"],
        key_responsibilities=["Design APIs", "Code reviews"],
        industry_domain="SaaS",
        keywords_for_ats=["python", "backend", "api"],
        summary_of_role="Senior backend engineer building platform services.",
    )


@pytest.fixture
def dummy_model():
    return DummyModel(name="test", value=42)


@pytest.fixture
def dummy_model_list():
    return [DummyModel(name="a", value=1), DummyModel(name="b", value=2)]


@pytest.fixture
def minimal_template_content():
    return "Hello {{ name }}!"


@pytest.fixture
def resume_template_content():
    return """\
# {{ personal.name }}
{% for job in experience %}
## {{ job.title }} at {{ job.company }}
{% for bullet in job.bullets %}
- {{ bullet }}
{% endfor %}
{% endfor %}"""
