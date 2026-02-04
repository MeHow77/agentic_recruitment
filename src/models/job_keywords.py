from typing import Literal

from pydantic import BaseModel, Field

SkillCategory = Literal["technical", "soft", "certification", "education"]
SkillImportance = Literal["required", "preferred"]


class SkillRequirement(BaseModel):
    skills: list[str] = Field(description="Skills in this group")
    category: SkillCategory = Field(description="Skill category")
    importance: SkillImportance = Field(description="Whether required or preferred")


class JobDescriptionKeywords(BaseModel):
    job_title: str = Field(description="Exact job title from the posting")
    seniority_level: str = Field(description="Seniority level (e.g. Junior, Mid, Senior, Lead, Staff, Principal)")
    years_of_experience: str = Field(description="Required years of experience (e.g. '3-5 years', '5+')")
    company_name: str = Field(description="Name of the hiring company")
    department_or_team: str = Field(description="Department or team name, if mentioned")
    skill_requirements: list[SkillRequirement] = Field(
        description="Categorized skill requirements from the posting"
    )
    key_responsibilities: list[str] = Field(description="Main responsibilities and duties")
    industry_domain: str = Field(description="Industry or domain the role operates in")
    keywords_for_ats: list[str] = Field(
        description="Top 20 keywords and phrases optimized for ATS matching",
        max_length=20,
    )
    summary_of_role: str = Field(description="A concise 2-3 sentence summary of the role")
