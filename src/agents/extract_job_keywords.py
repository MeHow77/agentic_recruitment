from src.llm.handler import LLMHandler
from src.models.job_keywords import JobDescriptionKeywords

EXTRACTION_PROMPT = """\
You are an expert recruiter and ATS optimization specialist.

Analyze the following job description and extract structured keyword data.
Be precise — only include information explicitly stated or strongly implied in the text.
If a field is not mentioned, use an empty string or empty list as appropriate.

For `keywords_for_ats`, select the top 20 most impactful keywords and phrases
that an applicant tracking system would use to score a resume against this job.

Job description:
---
{markdown_content}
---
"""


async def extract_job_keywords(
    markdown_content: str,
    llm_handler: LLMHandler,
) -> JobDescriptionKeywords:
    """Extract structured keywords from a job description markdown string."""
    prompt = EXTRACTION_PROMPT.format(markdown_content=markdown_content)
    return await llm_handler.generate_structured(prompt, JobDescriptionKeywords)
