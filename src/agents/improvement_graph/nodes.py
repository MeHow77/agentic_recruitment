"""Node implementations for the interactive improvement graph."""

from collections.abc import Callable
from copy import deepcopy

from langgraph.types import interrupt
from pydantic import BaseModel

from src.agents.improvement_graph.state import (
    GraphPhase,
    ImprovementGraphState,
    InterruptPayload,
    InterruptType,
)
from src.llm.provider import LLMProvider
from src.models.experience_data import ExperienceData
from src.models.improvement_session import (
    AchievementDiscovery,
    GapResponse,
    JobDeepDiveResult,
)
from src.prompts.prompter import Prompter


# --- Pydantic models for LLM responses ---


class GapQuestionResponse(BaseModel):
    question: str


class JobDeepDiveQuestions(BaseModel):
    questions: list[str]


class XYZRewriteResponse(BaseModel):
    x_accomplished: str
    y_measured_by: str
    z_by_doing: str
    bullet: str


class HumanizeResponse(BaseModel):
    bullet: str
    changes_made: str


# --- Node factory type ---

NodeFunc = Callable[[ImprovementGraphState], ImprovementGraphState]


# --- LLM Nodes (use closures to inject provider) ---


def make_generate_gap_question(provider: LLMProvider) -> NodeFunc:
    """Factory for gap question generation node."""

    async def generate_gap_question(
        state: ImprovementGraphState,
    ) -> ImprovementGraphState:
        gaps = state["skill_gaps"].gaps
        idx = state.get("current_gap_index", 0)
        gap = gaps[idx]

        prompt = Prompter.load("gap_question").format(
            skill=gap.skill,
            category=gap.category,
            importance=gap.importance,
            context=gap.context,
        )

        response = await provider.generate_structured(prompt, GapQuestionResponse)

        return {"pending_gap_question": response.question}

    return generate_gap_question


def make_generate_deep_dive_questions(provider: LLMProvider) -> NodeFunc:
    """Factory for job deep-dive question generation node."""

    async def generate_deep_dive_questions(
        state: ImprovementGraphState,
    ) -> ImprovementGraphState:
        job_idx = state["current_job_index"]
        job_entry = state["experience_data"].experience[job_idx]
        gap_responses = state.get("gap_responses", [])

        # Find relevant skills for this job
        relevant_skills = [
            gr.gap.skill
            for gr in gap_responses
            if gr.has_experience and job_idx in gr.relevant_jobs
        ]

        bullets_text = "\n".join(f"  - {b}" for b in job_entry.bullets)
        skills_text = ", ".join(relevant_skills) if relevant_skills else "None identified"

        prompt = Prompter.load("job_deep_dive").format(
            title=job_entry.title,
            company=job_entry.company,
            date=job_entry.date,
            bullets=bullets_text,
            relevant_skills=skills_text,
        )

        response = await provider.generate_structured(prompt, JobDeepDiveQuestions)

        return {
            "pending_questions": response.questions,
            "current_question_index": 0,
            "current_achievements": [],
        }

    return generate_deep_dive_questions


def make_generate_xyz_bullet(provider: LLMProvider) -> NodeFunc:
    """Factory for XYZ bullet generation node."""

    async def generate_xyz_bullet(
        state: ImprovementGraphState,
    ) -> ImprovementGraphState:
        user_input = state["human_response"]
        if not user_input or not isinstance(user_input, str) or not user_input.strip():
            # No input provided, skip
            return {"current_question_index": state["current_question_index"] + 1}

        job_idx = state["current_job_index"]
        job_entry = state["experience_data"].experience[job_idx]

        prompt = Prompter.load("xyz_rewrite").format(
            user_input=user_input,
            title=job_entry.title,
            company=job_entry.company,
        )

        response = await provider.generate_structured(prompt, XYZRewriteResponse)

        achievement = AchievementDiscovery(
            original_bullet_index=None,
            x_accomplished=response.x_accomplished,
            y_measured_by=response.y_measured_by,
            z_by_doing=response.z_by_doing,
            raw_user_input=user_input,
        )

        current_achievements = list(state.get("current_achievements", []))
        current_achievements.append(achievement)

        return {
            "current_achievements": current_achievements,
            "current_question_index": state["current_question_index"] + 1,
        }

    return generate_xyz_bullet


def make_refine_bullet(provider: LLMProvider) -> NodeFunc:
    """Factory for bullet refinement/humanization node."""

    async def refine_bullet(state: ImprovementGraphState) -> ImprovementGraphState:
        current_bullet = state["current_bullet"]
        feedback = state["human_response"]

        if not feedback or not isinstance(feedback, str):
            return {}

        prompt = Prompter.load("humanize_bullet").format(
            bullet=current_bullet,
            feedback=feedback,
        )

        response = await provider.generate_structured(prompt, HumanizeResponse)

        return {"current_bullet": response.bullet}

    return refine_bullet


# --- Human Interaction Nodes (use interrupt()) ---


def ask_gap_experience(state: ImprovementGraphState) -> ImprovementGraphState:
    """Interrupt to ask user about gap experience."""
    question = state["pending_gap_question"]
    gaps = state["skill_gaps"].gaps
    idx = state.get("current_gap_index", 0)
    gap = gaps[idx]

    payload: InterruptPayload = {
        "type": InterruptType.CONFIRM,
        "prompt": f"{question}\n\nDo you have experience with {gap.skill}?",
        "default": False,
        "context": {"gap_skill": gap.skill, "gap_index": idx},
    }

    response = interrupt(payload)

    return {"human_response": response}


def collect_gap_details(state: ImprovementGraphState) -> ImprovementGraphState:
    """Interrupt to collect details about gap experience."""
    gaps = state["skill_gaps"].gaps
    idx = state.get("current_gap_index", 0)
    gap = gaps[idx]
    experience_data = state["experience_data"]

    # Build job options for context
    job_options = [
        f"{i}: {e.title} at {e.company}"
        for i, e in enumerate(experience_data.experience)
    ]

    payload: InterruptPayload = {
        "type": InterruptType.TEXT_INPUT,
        "prompt": f"Please describe your experience with {gap.skill}:",
        "context": {
            "gap_skill": gap.skill,
            "job_options": job_options,
            "need_job_selection": True,
        },
    }

    response = interrupt(payload)

    return {"human_response": response}


def ask_deep_dive_question(state: ImprovementGraphState) -> ImprovementGraphState:
    """Interrupt to ask a deep-dive question."""
    questions = state["pending_questions"]
    q_idx = state["current_question_index"]

    if q_idx >= len(questions):
        return {}

    question = questions[q_idx]

    payload: InterruptPayload = {
        "type": InterruptType.TEXT_INPUT,
        "prompt": f"{question}\n\n(Press Enter to skip)",
        "context": {"question_index": q_idx},
    }

    response = interrupt(payload)

    return {"human_response": response}


def ask_additional_achievement(state: ImprovementGraphState) -> ImprovementGraphState:
    """Interrupt to ask for additional achievements."""
    job_idx = state["current_job_index"]
    job_entry = state["experience_data"].experience[job_idx]

    payload: InterruptPayload = {
        "type": InterruptType.TEXT_INPUT,
        "prompt": f"Any other achievements from {job_entry.title} at {job_entry.company} not mentioned above?\n\n(Press Enter to finish)",
        "context": {"job_index": job_idx, "is_additional": True},
    }

    response = interrupt(payload)

    return {"human_response": response}


def present_bullet_options(state: ImprovementGraphState) -> ImprovementGraphState:
    """Interrupt to present bullet for approval/edit/skip."""
    current_bullet = state["current_bullet"]
    achievement = state["current_achievement"]

    payload: InterruptPayload = {
        "type": InterruptType.SELECT,
        "prompt": f"Original input: {achievement.raw_user_input}\n\nXYZ version: {current_bullet}\n\nDoes this sound like you?",
        "options": ["Yes, looks good", "No, I want to edit", "Skip this bullet"],
        "context": {"bullet": current_bullet},
    }

    response = interrupt(payload)

    return {"human_response": response}


def collect_edit_feedback(state: ImprovementGraphState) -> ImprovementGraphState:
    """Interrupt to collect edit feedback for bullet."""
    payload: InterruptPayload = {
        "type": InterruptType.TEXT_INPUT,
        "prompt": "What would you like to change?",
        "context": {"current_bullet": state["current_bullet"]},
    }

    response = interrupt(payload)

    return {"human_response": response}


# --- State Management Nodes ---


def init_state(state: ImprovementGraphState) -> ImprovementGraphState:
    """Initialize graph state."""
    return {
        "phase": GraphPhase.GAP_EXPLORATION,
        "current_gap_index": 0,
        "gap_responses": [],
        "current_job_index": 0,
        "job_results": [],
        "humanization_job_index": 0,
        "humanization_achievement_index": 0,
    }


def store_gap_response(state: ImprovementGraphState) -> ImprovementGraphState:
    """Store gap response when user has no experience."""
    gaps = state["skill_gaps"].gaps
    idx = state.get("current_gap_index", 0)
    gap = gaps[idx]

    gap_response = GapResponse(
        gap=gap,
        has_experience=False,
        details="",
        relevant_jobs=[],
    )

    gap_responses = list(state.get("gap_responses", []))
    gap_responses.append(gap_response)

    return {
        "gap_responses": gap_responses,
        "current_gap_index": idx + 1,
    }


def store_gap_response_with_details(
    state: ImprovementGraphState,
) -> ImprovementGraphState:
    """Store gap response with user-provided details."""
    gaps = state["skill_gaps"].gaps
    idx = state.get("current_gap_index", 0)
    gap = gaps[idx]

    # The human_response should contain dict with details and relevant_jobs
    response_data = state.get("human_response", {})
    if isinstance(response_data, dict):
        details = response_data.get("details", "")
        relevant_jobs = response_data.get("relevant_jobs", [])
    else:
        details = str(response_data) if response_data else ""
        relevant_jobs = []

    gap_response = GapResponse(
        gap=gap,
        has_experience=True,
        details=details,
        relevant_jobs=relevant_jobs,
    )

    gap_responses = list(state.get("gap_responses", []))
    gap_responses.append(gap_response)

    return {
        "gap_responses": gap_responses,
        "current_gap_index": idx + 1,
    }


def start_job_deep_dive(state: ImprovementGraphState) -> ImprovementGraphState:
    """Initialize state for job deep-dive phase."""
    return {
        "phase": GraphPhase.JOB_DEEP_DIVE,
        "current_job_index": state.get("current_job_index", 0),
        "current_achievements": [],
    }


def finalize_job(state: ImprovementGraphState) -> ImprovementGraphState:
    """Bundle achievements into JobDeepDiveResult."""
    job_idx = state["current_job_index"]
    job_entry = state["experience_data"].experience[job_idx]
    achievements = state.get("current_achievements", [])

    result = JobDeepDiveResult(
        job_index=job_idx,
        original_entry=job_entry,
        achievements=achievements,
        enhanced_bullets=[],
    )

    job_results = list(state.get("job_results", []))
    job_results.append(result)

    return {
        "job_results": job_results,
        "current_job_index": job_idx + 1,
        "current_achievements": [],
    }


def prepare_humanization(state: ImprovementGraphState) -> ImprovementGraphState:
    """Prepare for humanization phase."""
    return {
        "phase": GraphPhase.HUMANIZATION,
        "humanization_job_index": 0,
        "humanization_achievement_index": 0,
    }


def prepare_bullet(state: ImprovementGraphState) -> ImprovementGraphState:
    """Set up next bullet for humanization."""
    job_idx = state["humanization_job_index"]
    ach_idx = state["humanization_achievement_index"]

    job_results = state.get("job_results", [])
    if job_idx >= len(job_results):
        return {}

    job_result = job_results[job_idx]
    if ach_idx >= len(job_result.achievements):
        return {}

    achievement = job_result.achievements[ach_idx]

    # Generate initial XYZ bullet
    initial_bullet = (
        f"{achievement.x_accomplished}, "
        f"measured by {achievement.y_measured_by}, "
        f"by {achievement.z_by_doing}"
    )

    return {
        "current_bullet": initial_bullet,
        "current_achievement": achievement,
    }


def save_bullet(state: ImprovementGraphState) -> ImprovementGraphState:
    """Save approved bullet to job result."""
    job_idx = state["humanization_job_index"]
    current_bullet = state["current_bullet"]

    job_results = list(state.get("job_results", []))
    job_result = job_results[job_idx]

    # Create new job result with updated bullets
    enhanced = list(job_result.enhanced_bullets)
    enhanced.append(current_bullet)

    updated_result = JobDeepDiveResult(
        job_index=job_result.job_index,
        original_entry=job_result.original_entry,
        achievements=job_result.achievements,
        enhanced_bullets=enhanced,
    )
    job_results[job_idx] = updated_result

    return {"job_results": job_results}


def advance_humanization(state: ImprovementGraphState) -> ImprovementGraphState:
    """Move to next bullet/job in humanization."""
    job_idx = state["humanization_job_index"]
    ach_idx = state["humanization_achievement_index"]

    job_results = state.get("job_results", [])
    if job_idx >= len(job_results):
        return {}

    job_result = job_results[job_idx]

    # Try next achievement in current job
    if ach_idx + 1 < len(job_result.achievements):
        return {"humanization_achievement_index": ach_idx + 1}

    # Move to next job
    return {
        "humanization_job_index": job_idx + 1,
        "humanization_achievement_index": 0,
    }


def apply_improvements(state: ImprovementGraphState) -> ImprovementGraphState:
    """Create final ExperienceData with improvements applied."""
    experience_data = state["experience_data"]
    job_results = state.get("job_results", [])

    result = deepcopy(experience_data)

    for job_result in job_results:
        # Combine original bullets with new enhanced ones
        original_bullets = list(job_result.original_entry.bullets)
        enhanced = job_result.enhanced_bullets

        if enhanced:
            # Add enhanced bullets to original
            result.experience[job_result.job_index].bullets = original_bullets + enhanced

    return {
        "phase": GraphPhase.COMPLETED,
        "final_experience_data": result,
    }
