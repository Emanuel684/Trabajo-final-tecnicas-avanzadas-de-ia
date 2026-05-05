from __future__ import annotations

from typing import Literal

from langgraph.graph import END, START, StateGraph

from src.activities.core import (
    check_sufficiency,
    diagnose_failure,
    evaluate_zones,
    explain_output,
    identify_zones,
    inject_external_signals,
    interpret_requirements,
    filter_constraints,
    score_alternatives,
    search_properties,
)
from src.evaluator import final_evaluator
from src.relaxation import relax_constraints
from src.state import RecommendationState


def route_after_sufficiency(state: RecommendationState) -> Literal["final_evaluator", "diagnose_failure"]:
    enough = len(state["final_recommendations"]) >= state["current_criteria"]["min_alternatives"]
    return "final_evaluator" if enough else "diagnose_failure"


def route_after_relax(state: RecommendationState) -> Literal["identify_zones", "final_evaluator"]:
    if state["iteration_count"] < state["max_iterations"]:
        return "identify_zones"
    return "final_evaluator"


def route_after_eval(state: RecommendationState) -> Literal["explain_output", "relax_constraints"]:
    if state["acceptance_status"] == "approved":
        return "explain_output"
    if state["iteration_count"] >= state["max_iterations"]:
        state["acceptance_status"] = "rejected"
        return "explain_output"
    return "relax_constraints"


def build_graph():
    graph = StateGraph(RecommendationState)

    graph.add_node("interpret_requirements", interpret_requirements)
    graph.add_node("identify_zones", identify_zones)
    graph.add_node("evaluate_zones", evaluate_zones)
    graph.add_node("inject_external_signals", inject_external_signals)
    graph.add_node("search_properties", search_properties)
    graph.add_node("filter_constraints", filter_constraints)
    graph.add_node("score_alternatives", score_alternatives)
    graph.add_node("check_sufficiency", check_sufficiency)
    graph.add_node("diagnose_failure", diagnose_failure)
    graph.add_node("relax_constraints", relax_constraints)
    graph.add_node("final_evaluator", final_evaluator)
    graph.add_node("explain_output", explain_output)

    graph.add_edge(START, "interpret_requirements")
    graph.add_edge("interpret_requirements", "identify_zones")
    graph.add_edge("identify_zones", "evaluate_zones")
    graph.add_edge("evaluate_zones", "inject_external_signals")
    graph.add_edge("inject_external_signals", "search_properties")
    graph.add_edge("search_properties", "filter_constraints")
    graph.add_edge("filter_constraints", "score_alternatives")
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
        route_after_relax,
        {
            "identify_zones": "identify_zones",
            "final_evaluator": "final_evaluator",
        },
    )
    graph.add_conditional_edges(
        "final_evaluator",
        route_after_eval,
        {
            "explain_output": "explain_output",
            "relax_constraints": "relax_constraints",
        },
    )
    graph.add_edge("explain_output", END)

    return graph.compile()
