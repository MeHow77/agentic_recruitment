from enum import Enum

from pydantic import BaseModel, Field

from src.models.experience_data import ExperienceEntry
from src.models.skill_gap import SkillGap


class SessionPhase(str, Enum):
    GAP_EXPLORATION = "gap_exploration"
    JOB_DEEP_DIVE = "job_deep_dive"
    HUMANIZATION = "humanization"
    COMPLETED = "completed"


class GapResponse(BaseModel):
    """User's response to a skill gap question."""

    gap: SkillGap
    has_experience: bool
    details: str = ""
    relevant_jobs: list[int] = Field(default_factory=list)


class AchievementDiscovery(BaseModel):
    """An achievement parsed into XYZ format."""

    original_bullet_index: int | None = None
    x_accomplished: str = Field(description="What was accomplished (outcome/impact)")
    y_measured_by: str = Field(description="How it was measured (metric/measurement)")
    z_by_doing: str = Field(description="How it was done (actions/methods/tools)")
    raw_user_input: str = Field(description="Original user input before parsing")


class JobDeepDiveResult(BaseModel):
    """Results from deep-diving into one job experience."""

    job_index: int
    original_entry: ExperienceEntry
    achievements: list[AchievementDiscovery] = Field(default_factory=list)
    enhanced_bullets: list[str] = Field(default_factory=list)


class ImprovementSession(BaseModel):
    """Internal state tracking for an interactive improvement session."""

    phase: SessionPhase = SessionPhase.GAP_EXPLORATION
    gap_responses: list[GapResponse] = Field(default_factory=list)
    job_results: list[JobDeepDiveResult] = Field(default_factory=list)
