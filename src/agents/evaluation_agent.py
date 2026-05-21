from __future__ import annotations

from typing import Any, Dict, List

from src.agents.utils import append_history, append_trace
from src.state import RecommendationState
from src.tools.housing_tools import apply_relaxation, diagnose_failure as diagnose_with_tools


def diagnose_failure(state: RecommendationState) -> RecommendationState:
    diagnosis = diagnose_with_tools(
        criteria=state["current_criteria"],
        zone_candidates=state["zone_candidates"],
        property_results=state["property_results"],
        filtered_properties=state["filtered_properties"],
        scored_alternatives=state["scored_alternatives"],
        rejection_counts=state["sufficiency_status"].get("rejection_counts", {}),
        iteration=state["iteration_count"],
    )
    state["failure_diagnosis"] = diagnosis
    append_trace(state, "evaluation_agent", "diagnose_failure", diagnosis)
    append_history(state, "diagnose_failure", reason=diagnosis["reason"])
    return state


def relax_constraints(state: RecommendationState) -> RecommendationState:
    state["iteration_count"] += 1
    state["relaxation_level"] += 1
    updated_criteria, log_entry = apply_relaxation(
        criteria=state["current_criteria"],
        original_criteria=state["original_criteria"],
        iteration=state["iteration_count"],
        relaxation_level=state["relaxation_level"],
        failure_diagnosis=state["failure_diagnosis"],
    )
    state["current_criteria"] = updated_criteria
    state["relaxation_log"].append(log_entry)
    append_trace(state, "evaluation_agent", "relax_constraints", log_entry)
    append_history(
        state,
        "relax_constraints",
        field=log_entry["field"],
        new_value=log_entry["new_value"],
    )
    return state


def final_evaluator(state: RecommendationState) -> RecommendationState:
    required = state["current_criteria"]["min_alternatives"]
    min_score = state["current_criteria"]["min_score"]
    recommendations = state["final_recommendations"]

    if len(recommendations) < required:
        state["acceptance_status"] = "retry"
        state["failure_diagnosis"] = {
            "iteration": state["iteration_count"],
            "reason": (
                f"Solo se encontraron {len(recommendations)} alternativas; "
                f"se requieren {required}."
            ),
        }
    elif any(item["score"] < min_score for item in recommendations):
        state["acceptance_status"] = "retry"
        state["failure_diagnosis"] = {
            "iteration": state["iteration_count"],
            "reason": "Una alternativa no cumple el score minimo vigente.",
        }
    else:
        state["acceptance_status"] = "approved"
        state["failure_diagnosis"] = {}

    if state["acceptance_status"] == "retry" and state["iteration_count"] >= state["max_iterations"]:
        state["acceptance_status"] = "rejected"

    append_trace(
        state,
        "evaluation_agent",
        "final_evaluation",
        {
            "acceptance_status": state["acceptance_status"],
            "recommendation_count": len(recommendations),
            "failure_diagnosis": state["failure_diagnosis"],
        },
    )
    append_history(
        state,
        "final_evaluator",
        acceptance_status=state["acceptance_status"],
        recommendation_count=len(recommendations),
    )
    return state


def explain_output(state: RecommendationState) -> RecommendationState:
    explained: List[Dict[str, Any]] = []
    for rank, item in enumerate(state["final_recommendations"], start=1):
        explained.append(
            {
                "rank": rank,
                "property_id": item["id"],
                "zone": item["zone"],
                "price_cop": item["price_cop"],
                "area_m2": item["area_m2"],
                "amenities": item["amenities"],
                "score": item["score"],
                "score_breakdown": item["score_breakdown"],
                "why": item["explanation"],
                "criteria_snapshot": dict(state["current_criteria"]),
            }
        )
    state["final_recommendations"] = explained
    append_trace(
        state,
        "evaluation_agent",
        "explain_output",
        {
            "output_count": len(explained),
            "acceptance_status": state["acceptance_status"],
        },
    )
    append_history(state, "explain_output", output_count=len(explained))
    return state
