from pydantic import BaseModel, Field


class JobDescriptionKeywords(BaseModel):
    job_title: str = Field(description="Exact job title from the posting")
    seniority_level: str = Field(description="Seniority level (e.g. Junior, Mid, Senior, Lead, Staff, Principal)")
    years_of_experience: str = Field(description="Required years of experience (e.g. '3-5 years', '5+')")
    company_name: str = Field(description="Name of the hiring company")
    department_or_team: str = Field(description="Department or team name, if mentioned")
    required_technical_skills: list[str] = Field(description="Technical skills explicitly required")
    preferred_technical_skills: list[str] = Field(description="Technical skills listed as nice-to-have or preferred")
    required_soft_skills: list[str] = Field(description="Soft skills explicitly required")
    required_education: str = Field(description="Minimum education requirement (e.g. 'Bachelor's in CS or equivalent')")
    preferred_certifications: list[str] = Field(description="Certifications listed as preferred or required")
    key_responsibilities: list[str] = Field(description="Main responsibilities and duties")
    industry_domain: str = Field(description="Industry or domain the role operates in")
    keywords_for_ats: list[str] = Field(
        description="Top 20 keywords and phrases optimized for ATS matching",
        max_length=20,
    )
    summary_of_role: str = Field(description="A concise 2-3 sentence summary of the role")
