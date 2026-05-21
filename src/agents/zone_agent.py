from __future__ import annotations

from src.agents.utils import append_history, append_trace
from src.state import RecommendationState
from src.tools.housing_tools import evaluate_zone_candidates, identify_zone_candidates


def identify_zones(state: RecommendationState) -> RecommendationState:
    candidates = identify_zone_candidates(state["current_criteria"])
    state["zone_candidates"] = candidates
    append_trace(
        state,
        "zone_agent",
        "identify_candidate_zones",
        {
            "candidate_count": len(candidates),
            "zones": [zone["name"] for zone in candidates],
        },
    )
    append_history(
        state,
        "identify_zones",
        candidate_count=len(candidates),
        min_safety=state["current_criteria"]["min_safety"],
    )
    return state


def evaluate_zones(state: RecommendationState) -> RecommendationState:
    evaluations = evaluate_zone_candidates(state["zone_candidates"])
    state["zone_evaluations"] = evaluations
    append_trace(
        state,
        "zone_agent",
        "evaluate_candidate_zones",
        {
            "evaluated_count": len(evaluations),
            "top_zone": evaluations[0]["zone"] if evaluations else None,
        },
    )
    append_history(state, "evaluate_zones", evaluated_count=len(evaluations))
    return state
