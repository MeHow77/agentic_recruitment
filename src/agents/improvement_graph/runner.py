"""Runner that orchestrates the improvement graph with Console integration."""

from uuid import uuid4

from langgraph.types import Command

from src.agents.improvement_graph.graph import build_improvement_graph
from src.agents.improvement_graph.state import (
    GraphPhase,
    ImprovementGraphState,
    InterruptPayload,
    InterruptType,
)
from src.cli.console import Console
from src.llm.provider import LLMProvider
from src.models.experience_data import ExperienceData
from src.models.skill_gap import SkillGapAnalysis


async def handle_interrupt(
    payload: InterruptPayload,
    console: Console,
    experience_data: ExperienceData | None = None,
) -> str | bool | dict:
    """Translate an interrupt payload into Console interactions."""
    interrupt_type = payload.get("type")
    prompt = payload.get("prompt", "")
    context = payload.get("context", {})

    if interrupt_type == InterruptType.CONFIRM:
        default = payload.get("default", False)
        return await console.confirm(prompt, default=default)

    elif interrupt_type == InterruptType.SELECT:
        options = payload.get("options", [])
        return await console.select(prompt, options)

    elif interrupt_type == InterruptType.TEXT_INPUT:
        # Check if we also need job selection (for gap details)
        need_job_selection = context.get("need_job_selection", False)

        if need_job_selection and experience_data:
            # Collect details first
            details = await console.input(prompt)

            # Then ask for relevant jobs
            job_options = context.get("job_options", [])
            if job_options:
                console.print(
                    "\nWhich jobs involved this skill? (Enter comma-separated numbers)"
                )
                for opt in job_options:
                    console.print(f"  {opt}")

                job_input = await console.input("Job numbers (e.g., 0,2): ")
                relevant_jobs = []
                if job_input.strip():
                    try:
                        relevant_jobs = [
                            int(x.strip()) for x in job_input.split(",") if x.strip()
                        ]
                    except ValueError:
                        relevant_jobs = []

                return {"details": details, "relevant_jobs": relevant_jobs}

            return {"details": details, "relevant_jobs": []}

        return await console.input(prompt)

    return ""


async def run_improvement_graph(
    experience_data: ExperienceData,
    skill_gaps: SkillGapAnalysis,
    provider: LLMProvider,
    console: Console,
) -> ExperienceData:
    """Run the improvement graph with Console-based human interaction."""
    graph = build_improvement_graph(provider)
    config = {"configurable": {"thread_id": uuid4().hex}}

    # Print header
    console.print("\n=== Interactive Resume Improvement ===\n", style="bold")
    console.print(
        "I'll help you improve your resume by exploring skill gaps and uncovering achievements.\n"
    )

    # Initial state
    initial_state: ImprovementGraphState = {
        "experience_data": experience_data,
        "skill_gaps": skill_gaps,
        "phase": GraphPhase.INIT,
        "current_gap_index": 0,
        "gap_responses": [],
        "current_job_index": 0,
        "job_results": [],
        "humanization_job_index": 0,
        "humanization_achievement_index": 0,
    }

    current_input: ImprovementGraphState | Command = initial_state
    last_phase = GraphPhase.INIT

    while True:
        # Run graph until interrupt or completion
        result = await graph.ainvoke(current_input, config)

        # Check graph state
        state = graph.get_state(config)

        # Print phase transitions
        current_phase = result.get("phase", GraphPhase.INIT)
        if current_phase != last_phase:
            if current_phase == GraphPhase.GAP_EXPLORATION:
                console.print(
                    "--- Phase 1: Skill Gap Exploration ---\n", style="bold"
                )
            elif current_phase == GraphPhase.JOB_DEEP_DIVE:
                console.print(
                    "\n--- Phase 2: Job Experience Deep-Dive ---\n", style="bold"
                )
                # Show job info when entering deep-dive
                job_idx = result.get("current_job_index", 0)
                if job_idx < len(experience_data.experience):
                    job = experience_data.experience[job_idx]
                    console.print(f"\n>> {job.title} at {job.company} ({job.date})")
                    console.print("Current bullets:")
                    for i, bullet in enumerate(job.bullets):
                        console.print(f"  {i}. {bullet}")
            elif current_phase == GraphPhase.HUMANIZATION:
                console.print("\n--- Phase 3: Bullet Refinement ---\n", style="bold")
            last_phase = current_phase

        # Check if there are pending tasks (interrupts)
        if not state.next:
            # No pending nodes - graph completed
            break

        # Get interrupt value from the pending task
        if state.tasks and state.tasks[0].interrupts:
            interrupt_value = state.tasks[0].interrupts[0].value

            # Show context-specific info before interrupt
            _print_interrupt_context(interrupt_value, result, console, experience_data)

            # Handle the interrupt via Console
            response = await handle_interrupt(
                interrupt_value, console, experience_data
            )

            # Resume with the response
            current_input = Command(resume=response)
        else:
            # No interrupts but graph not done - shouldn't happen
            break

    # Return final result
    final_data = result.get("final_experience_data")
    if final_data:
        return final_data

    return experience_data


def _print_interrupt_context(
    payload: InterruptPayload,
    state: ImprovementGraphState,
    console: Console,
    experience_data: ExperienceData,
) -> None:
    """Print relevant context before an interrupt."""
    context = payload.get("context", {})
    interrupt_type = payload.get("type")

    # Show job info when starting deep-dive questions
    if context.get("question_index") == 0 and interrupt_type == InterruptType.TEXT_INPUT:
        job_idx = state.get("current_job_index", 0)
        if job_idx < len(experience_data.experience):
            job = experience_data.experience[job_idx]
            # Check if this is the first question for a new job
            q_idx = context.get("question_index", 0)
            if q_idx == 0:
                console.print(f"\n>> {job.title} at {job.company} ({job.date})")
                console.print("Current bullets:")
                for i, bullet in enumerate(job.bullets):
                    console.print(f"  {i}. {bullet}")

    # Show bullet context during humanization
    if interrupt_type == InterruptType.SELECT and "bullet" in context:
        achievement = state.get("current_achievement")
        if achievement:
            job_idx = state.get("humanization_job_index", 0)
            job_results = state.get("job_results", [])
            if job_idx < len(job_results):
                job_result = job_results[job_idx]
                console.print(
                    f"\n>> Refining bullets for: {job_result.original_entry.title} "
                    f"at {job_result.original_entry.company}"
                )
