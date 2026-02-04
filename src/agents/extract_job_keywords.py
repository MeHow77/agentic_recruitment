from src.llm.provider import LLMProvider
from src.models.job_keywords import JobDescriptionKeywords
from src.prompts.prompter import Prompter


async def extract_job_keywords(
    markdown_content: str,
    provider: LLMProvider,
) -> JobDescriptionKeywords:
    """Extract structured keywords from a job description markdown string."""
    prompt = Prompter.load("extract_job_keywords").format(markdown_content=markdown_content)
    return await provider.generate_structured(prompt, JobDescriptionKeywords)
