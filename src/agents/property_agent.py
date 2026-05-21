from __future__ import annotations

from src.agents.utils import append_history, append_trace
from src.state import RecommendationState
from src.tools.housing_tools import (
    filter_properties,
    score_properties,
    search_properties_for_zones,
    select_accepted_alternatives,
)


def search_properties(state: RecommendationState) -> RecommendationState:
    properties = search_properties_for_zones(state["zone_evaluations"])
    state["property_results"] = properties
    append_trace(
        state,
        "property_agent",
        "search_properties_by_zone",
        {
            "properties_found": len(properties),
            "zones": sorted({prop["zone"] for prop in properties}),
        },
    )
    append_history(state, "search_properties", properties_found=len(properties))
    return state


def filter_candidate_properties(state: RecommendationState) -> RecommendationState:
    filtered, rejection_counts = filter_properties(
        state["property_results"],
        state["current_criteria"],
    )
    state["filtered_properties"] = filtered
    state["sufficiency_status"]["rejection_counts"] = rejection_counts
    append_trace(
        state,
        "property_agent",
        "filter_constraints",
        {
            "input_count": len(state["property_results"]),
            "filtered_count": len(filtered),
            "rejection_counts": rejection_counts,
        },
    )
    append_history(state, "filter_constraints", filtered_count=len(filtered))
    return state


def score_alternatives(state: RecommendationState) -> RecommendationState:
    scored = score_properties(
        state["filtered_properties"],
        state["zone_evaluations"],
        state["external_signals"],
        state["current_criteria"],
    )
    state["scored_alternatives"] = scored
    append_trace(
        state,
        "property_agent",
        "score_alternatives",
        {
            "scored_count": len(scored),
            "best_score": scored[0]["score"] if scored else None,
        },
    )
    append_history(state, "score_alternatives", scored_count=len(scored))
    return state


def check_sufficiency(state: RecommendationState) -> RecommendationState:
    accepted = select_accepted_alternatives(
        state["scored_alternatives"],
        state["current_criteria"],
    )
    required = state["current_criteria"]["min_alternatives"]
    state["final_recommendations"] = accepted
    state["sufficiency_status"].update(
        {
            "accepted_count": len(accepted),
            "required": required,
            "is_sufficient": len(accepted) >= required,
            "min_score": state["current_criteria"]["min_score"],
        }
    )
    append_trace(
        state,
        "property_agent",
        "check_sufficiency",
        dict(state["sufficiency_status"]),
    )
    append_history(
        state,
        "check_sufficiency",
        accepted_count=len(accepted),
        required=required,
    )
    return state
