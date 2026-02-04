from pydantic import BaseModel, Field

from src.models.job_keywords import SkillCategory, SkillImportance


class SkillGap(BaseModel):
    skill: str = Field(description="The missing or underrepresented skill")
    category: SkillCategory = Field(description="Skill category")
    importance: SkillImportance = Field(description="Whether required or preferred by the posting")
    context: str = Field(description="Why this gap matters for the specific role")


class SkillGapAnalysis(BaseModel):
    gaps: list[SkillGap] = Field(description="Identified gaps between resume and job requirements")
