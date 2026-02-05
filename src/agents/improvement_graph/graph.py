"""Graph builder for the interactive improvement workflow."""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.agents.improvement_graph.edges import (
    route_after_deep_dive_questions,
    route_after_gap_advance,
    route_after_gap_experience,
    route_after_humanization_advance,
    route_after_job_advance,
    route_after_prepare_bullet,
    route_after_prepare_humanization,
    route_after_xyz_generation,
    route_bullet_response,
    route_initial,
    route_after_additional,
)
from src.agents.improvement_graph.nodes import (
    advance_humanization,
    apply_improvements,
    ask_additional_achievement,
    ask_deep_dive_question,
    ask_gap_experience,
    collect_edit_feedback,
    collect_gap_details,
    finalize_job,
    init_state,
    make_generate_deep_dive_questions,
    make_generate_gap_question,
    make_generate_xyz_bullet,
    make_refine_bullet,
    prepare_bullet,
    prepare_humanization,
    present_bullet_options,
    save_bullet,
    start_job_deep_dive,
    store_gap_response,
    store_gap_response_with_details,
)
from src.agents.improvement_graph.state import ImprovementGraphState
from src.llm.provider import LLMProvider


def build_improvement_graph(provider: LLMProvider) -> CompiledStateGraph:
    """Build and compile the improvement workflow graph."""
    builder = StateGraph(ImprovementGraphState)

    # --- Add all nodes ---

    # Initialization
    builder.add_node("init_state", init_state)

    # Gap exploration nodes
    builder.add_node("generate_gap_question", make_generate_gap_question(provider))
    builder.add_node("ask_gap_experience", ask_gap_experience)
    builder.add_node("collect_gap_details", collect_gap_details)
    builder.add_node("store_gap_response", store_gap_response)
    builder.add_node("store_gap_response_with_details", store_gap_response_with_details)

    # Job deep-dive nodes
    builder.add_node("start_job_deep_dive", start_job_deep_dive)
    builder.add_node(
        "generate_deep_dive_questions", make_generate_deep_dive_questions(provider)
    )
    builder.add_node("ask_deep_dive_question", ask_deep_dive_question)
    builder.add_node("generate_xyz_bullet", make_generate_xyz_bullet(provider))
    builder.add_node("ask_additional_achievement", ask_additional_achievement)
    builder.add_node(
        "generate_xyz_from_additional", make_generate_xyz_bullet(provider)
    )
    builder.add_node("finalize_job", finalize_job)

    # Humanization nodes
    builder.add_node("prepare_humanization", prepare_humanization)
    builder.add_node("prepare_bullet", prepare_bullet)
    builder.add_node("present_bullet_options", present_bullet_options)
    builder.add_node("collect_edit_feedback", collect_edit_feedback)
    builder.add_node("refine_bullet", make_refine_bullet(provider))
    builder.add_node("save_bullet", save_bullet)
    builder.add_node("advance_humanization", advance_humanization)

    # Final
    builder.add_node("apply_improvements", apply_improvements)

    # --- Define edges ---

    # Entry point
    builder.add_edge(START, "init_state")
    builder.add_conditional_edges("init_state", route_initial)

    # Gap exploration flow
    builder.add_edge("generate_gap_question", "ask_gap_experience")
    builder.add_conditional_edges("ask_gap_experience", route_after_gap_experience)
    builder.add_edge("collect_gap_details", "store_gap_response_with_details")
    builder.add_conditional_edges("store_gap_response", route_after_gap_advance)
    builder.add_conditional_edges(
        "store_gap_response_with_details", route_after_gap_advance
    )

    # Job deep-dive flow
    builder.add_edge("start_job_deep_dive", "generate_deep_dive_questions")
    builder.add_conditional_edges(
        "generate_deep_dive_questions", route_after_deep_dive_questions
    )
    builder.add_edge("ask_deep_dive_question", "generate_xyz_bullet")
    builder.add_conditional_edges("generate_xyz_bullet", route_after_xyz_generation)
    builder.add_conditional_edges("ask_additional_achievement", route_after_additional)
    builder.add_edge("generate_xyz_from_additional", "ask_additional_achievement")
    builder.add_conditional_edges("finalize_job", route_after_job_advance)

    # Humanization flow
    builder.add_conditional_edges(
        "prepare_humanization", route_after_prepare_humanization
    )
    builder.add_conditional_edges("prepare_bullet", route_after_prepare_bullet)
    builder.add_conditional_edges("present_bullet_options", route_bullet_response)
    builder.add_edge("collect_edit_feedback", "refine_bullet")
    builder.add_edge("refine_bullet", "present_bullet_options")
    builder.add_edge("save_bullet", "advance_humanization")
    builder.add_conditional_edges(
        "advance_humanization", route_after_humanization_advance
    )

    # Final
    builder.add_edge("apply_improvements", END)

    # Compile with checkpointer for interrupt/resume support
    return builder.compile(checkpointer=MemorySaver())
