"""Conditional routing functions for the improvement graph."""

from typing import Literal

from src.agents.improvement_graph.state import ImprovementGraphState


def route_initial(
    state: ImprovementGraphState,
) -> Literal["generate_gap_question", "start_job_deep_dive"]:
    """Route from start based on whether there are skill gaps."""
    skill_gaps = state.get("skill_gaps")
    if skill_gaps and skill_gaps.gaps:
        return "generate_gap_question"
    return "start_job_deep_dive"


def route_after_gap_experience(
    state: ImprovementGraphState,
) -> Literal["collect_gap_details", "store_gap_response"]:
    """Route based on whether user has experience with gap."""
    has_experience = state.get("human_response", False)
    if has_experience:
        return "collect_gap_details"
    return "store_gap_response"


def route_after_gap_advance(
    state: ImprovementGraphState,
) -> Literal["generate_gap_question", "start_job_deep_dive"]:
    """Route after processing a gap - more gaps or move to job deep-dive."""
    current_idx = state.get("current_gap_index", 0)
    skill_gaps = state.get("skill_gaps")

    if skill_gaps and current_idx < len(skill_gaps.gaps):
        return "generate_gap_question"
    return "start_job_deep_dive"


def route_after_deep_dive_questions(
    state: ImprovementGraphState,
) -> Literal["ask_deep_dive_question", "ask_additional_achievement"]:
    """Route after generating questions - ask first or go to additional."""
    questions = state.get("pending_questions", [])
    if questions:
        return "ask_deep_dive_question"
    return "ask_additional_achievement"


def route_after_xyz_generation(
    state: ImprovementGraphState,
) -> Literal["ask_deep_dive_question", "ask_additional_achievement"]:
    """Route after generating XYZ bullet - more questions or additional."""
    q_idx = state.get("current_question_index", 0)
    questions = state.get("pending_questions", [])

    if q_idx < len(questions):
        return "ask_deep_dive_question"
    return "ask_additional_achievement"


def route_after_additional(
    state: ImprovementGraphState,
) -> Literal["generate_xyz_from_additional", "finalize_job"]:
    """Route after asking for additional achievements."""
    response = state.get("human_response", "")
    if response and isinstance(response, str) and response.strip():
        return "generate_xyz_from_additional"
    return "finalize_job"


def route_after_job_advance(
    state: ImprovementGraphState,
) -> Literal["generate_deep_dive_questions", "prepare_humanization"]:
    """Route after finalizing a job - more jobs or start humanization."""
    current_idx = state.get("current_job_index", 0)
    experience_data = state.get("experience_data")

    if experience_data and current_idx < len(experience_data.experience):
        return "generate_deep_dive_questions"
    return "prepare_humanization"


def route_after_prepare_humanization(
    state: ImprovementGraphState,
) -> Literal["prepare_bullet", "apply_improvements"]:
    """Route after preparing humanization - has bullets to refine or done."""
    job_results = state.get("job_results", [])

    # Check if there are any achievements to humanize
    for job_result in job_results:
        if job_result.achievements:
            return "prepare_bullet"

    return "apply_improvements"


def route_after_prepare_bullet(
    state: ImprovementGraphState,
) -> Literal["present_bullet_options", "advance_humanization"]:
    """Route after preparing a bullet - show options or advance."""
    current_bullet = state.get("current_bullet")
    if current_bullet:
        return "present_bullet_options"
    return "advance_humanization"


def route_bullet_response(
    state: ImprovementGraphState,
) -> Literal["save_bullet", "collect_edit_feedback", "advance_humanization"]:
    """Route based on user's response to bullet presentation."""
    response = state.get("human_response", "")

    if response == "Yes, looks good":
        return "save_bullet"
    elif response == "Skip this bullet":
        return "advance_humanization"
    else:  # "No, I want to edit"
        return "collect_edit_feedback"


def route_after_humanization_advance(
    state: ImprovementGraphState,
) -> Literal["prepare_bullet", "apply_improvements"]:
    """Route after advancing humanization - more bullets or done."""
    job_idx = state.get("humanization_job_index", 0)
    ach_idx = state.get("humanization_achievement_index", 0)
    job_results = state.get("job_results", [])

    if job_idx >= len(job_results):
        return "apply_improvements"

    job_result = job_results[job_idx]
    if ach_idx < len(job_result.achievements):
        return "prepare_bullet"

    return "apply_improvements"
