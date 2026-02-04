from src.llm.provider import LLMProvider
from src.models.experience_data import ExperienceData
from src.models.job_keywords import JobDescriptionKeywords
from src.models.skill_gap import SkillGapAnalysis
from src.prompts.prompter import Prompter


async def analyze_skill_gaps(
    experience_data: ExperienceData,
    job_keywords: JobDescriptionKeywords,
    provider: LLMProvider,
) -> SkillGapAnalysis:
    """Identify gaps between a candidate's resume and job requirements."""
    prompt = Prompter.load("analyze_skill_gaps").format(
        experience_data=experience_data.model_dump_json(indent=2),
        job_keywords=job_keywords.model_dump_json(indent=2),
    )
    return await provider.generate_structured(prompt, SkillGapAnalysis)
