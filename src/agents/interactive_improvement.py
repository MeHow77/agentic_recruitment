"""Interactive resume improvement workflow.

This module provides the public interface for the interactive improvement flow.
Implementation is delegated to the LangGraph-based improvement_graph package.
"""

from src.agents.improvement_graph.runner import run_improvement_graph
from src.cli.console import Console
from src.llm.provider import LLMProvider
from src.models.experience_data import ExperienceData
from src.models.skill_gap import SkillGapAnalysis


async def run_interactive_improvement(
    experience_data: ExperienceData,
    skill_gaps: SkillGapAnalysis,
    provider: LLMProvider,
    console: Console,
) -> ExperienceData:
    """Run the interactive improvement workflow.

    This orchestrates a multi-phase conversation with the user to:
    1. Explore skill gaps and gather relevant experience
    2. Deep-dive into job experiences to uncover achievements
    3. Humanize and refine achievement bullets

    Args:
        experience_data: The user's existing resume experience data
        skill_gaps: Analysis of gaps between resume and job requirements
        provider: LLM provider for generating questions and formatting
        console: Console interface for user interaction

    Returns:
        Updated ExperienceData with enhanced bullets
    """
    return await run_improvement_graph(
        experience_data=experience_data,
        skill_gaps=skill_gaps,
        provider=provider,
        console=console,
    )
