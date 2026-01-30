from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field

from src.models.job_keywords import JobDescriptionKeywords


class JobKeywordResult(BaseModel):
    source_url: str = Field(description="URL the keywords were extracted from")
    keywords: JobDescriptionKeywords


class ExtractionRun(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    results: list[JobKeywordResult] = Field(default_factory=list)
