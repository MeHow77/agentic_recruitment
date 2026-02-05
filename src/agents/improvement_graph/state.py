"""Graph state schema for the interactive improvement workflow."""

from enum import Enum
from typing import TypedDict

from src.models.experience_data import ExperienceData
from src.models.improvement_session import (
    AchievementDiscovery,
    GapResponse,
    JobDeepDiveResult,
)
from src.models.skill_gap import SkillGapAnalysis


class GraphPhase(str, Enum):
    INIT = "init"
    GAP_EXPLORATION = "gap_exploration"
    JOB_DEEP_DIVE = "job_deep_dive"
    HUMANIZATION = "humanization"
    COMPLETED = "completed"


class InterruptType(str, Enum):
    """Types of interrupts for human interaction."""

    CONFIRM = "confirm"
    TEXT_INPUT = "text_input"
    SELECT = "select"


class InterruptPayload(TypedDict, total=False):
    """Payload for human interaction interrupts."""

    type: InterruptType
    prompt: str
    # For confirm
    default: bool
    # For select
    options: list[str]
    # Additional context
    context: dict


class ImprovementGraphState(TypedDict, total=False):
    """State schema for the improvement graph."""

    # Inputs
    experience_data: ExperienceData
    skill_gaps: SkillGapAnalysis

    # Phase tracking
    phase: GraphPhase

    # Gap exploration
    current_gap_index: int
    gap_responses: list[GapResponse]
    pending_gap_question: str | None

    # Job deep-dive
    current_job_index: int
    job_results: list[JobDeepDiveResult]
    pending_questions: list[str]
    current_question_index: int
    current_achievements: list[AchievementDiscovery]

    # Humanization
    humanization_job_index: int
    humanization_achievement_index: int
    current_bullet: str | None
    current_achievement: AchievementDiscovery | None

    # Human interaction responses (populated after interrupt resume)
    human_response: str | bool | None

    # Output
    final_experience_data: ExperienceData | None
