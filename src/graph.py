from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph

from src.agents.evaluation_agent import (
    diagnose_failure,
    explain_output,
    final_evaluator,
    relax_constraints,
)
from src.agents.property_agent import (
    check_sufficiency,
    filter_candidate_properties,
    score_alternatives,
    search_properties,
)
from src.agents.requirements_agent import interpret_requirements
from src.agents.signals_agent import incorporate_external_signals
from src.agents.zone_agent import evaluate_zones, identify_zones
from src.state import RecommendationState


def route_after_sufficiency(
    state: RecommendationState,
) -> Literal["final_evaluator", "diagnose_failure"]:
    if state["sufficiency_status"].get("is_sufficient"):
        return "final_evaluator"
    if state["iteration_count"] >= state["max_iterations"]:
        return "final_evaluator"
    return "diagnose_failure"


def route_after_relaxation(
    state: RecommendationState,
) -> Literal["identify_zones", "final_evaluator"]:
    if state["iteration_count"] <= state["max_iterations"]:
        return "identify_zones"
    return "final_evaluator"


def route_after_final_evaluation(
    state: RecommendationState,
) -> Literal["explain_output", "relax_constraints"]:
    if state["acceptance_status"] in {"approved", "rejected"}:
        return "explain_output"
    if state["iteration_count"] >= state["max_iterations"]:
        return "explain_output"
    return "relax_constraints"


def build_graph():
    graph = StateGraph(RecommendationState)

    graph.add_node("interpret_requirements", interpret_requirements)
    graph.add_node("identify_zones", identify_zones)
    graph.add_node("evaluate_zones", evaluate_zones)
    graph.add_node("incorporate_external_signals", incorporate_external_signals)
    graph.add_node("search_properties", search_properties)
    graph.add_node("filter_candidate_properties", filter_candidate_properties)
    graph.add_node("score_alternatives", score_alternatives)
    graph.add_node("check_sufficiency", check_sufficiency)
    graph.add_node("diagnose_failure", diagnose_failure)
    graph.add_node("relax_constraints", relax_constraints)
    graph.add_node("final_evaluator", final_evaluator)
    graph.add_node("explain_output", explain_output)

    graph.add_edge(START, "interpret_requirements")
    graph.add_edge("interpret_requirements", "identify_zones")
    graph.add_edge("identify_zones", "evaluate_zones")
    graph.add_edge("evaluate_zones", "incorporate_external_signals")
    graph.add_edge("incorporate_external_signals", "search_properties")
    graph.add_edge("search_properties", "filter_candidate_properties")
    graph.add_edge("filter_candidate_properties", "score_alternatives")
    graph.add_edge("score_alternatives", "check_sufficiency")
    graph.add_conditional_edges(
        "check_sufficiency",
        route_after_sufficiency,
        {
            "final_evaluator": "final_evaluator",
            "diagnose_failure": "diagnose_failure",
        },
    )
    graph.add_edge("diagnose_failure", "relax_constraints")
    graph.add_conditional_edges(
        "relax_constraints",
        route_after_relaxation,
        {
            "identify_zones": "identify_zones",
            "final_evaluator": "final_evaluator",
        },
    )
    graph.add_conditional_edges(
        "final_evaluator",
        route_after_final_evaluation,
        {
            "explain_output": "explain_output",
            "relax_constraints": "relax_constraints",
        },
    )
    graph.add_edge("explain_output", END)

    return graph.compile()
