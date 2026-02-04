from src.llm.provider import LLMProvider
from src.models.experience_data import ExperienceData
from src.models.job_keywords import JobDescriptionKeywords
from src.models.skill_gap import SkillGapAnalysis
from src.prompts.prompter import Prompter


async def adjust_data(
    experience_data: ExperienceData,
    job_keywords: JobDescriptionKeywords,
    skill_gaps: SkillGapAnalysis,
    provider: LLMProvider,
) -> ExperienceData:
    """Tailor resume data for a specific job posting. Same type in, same type out."""
    prompt = Prompter.load("adjust_data").format(
        experience_data=experience_data.model_dump_json(indent=2),
        job_keywords=job_keywords.model_dump_json(indent=2),
        skill_gaps=skill_gaps.model_dump_json(indent=2),
    )
    return await provider.generate_structured(prompt, ExperienceData)
