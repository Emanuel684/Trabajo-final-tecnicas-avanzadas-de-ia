from __future__ import annotations

from src.state import RecommendationState


def final_evaluator(state: RecommendationState) -> RecommendationState:
    min_items = state["current_criteria"]["min_alternatives"]
    min_score = state["current_criteria"]["min_score"]
    recommendations = state["final_recommendations"]

    if len(recommendations) < min_items:
        state["acceptance_status"] = "retry"
        state["failure_diagnosis"] = {
            "iteration": state["iteration_count"],
            "reason": f"Solo se encontraron {len(recommendations)} alternativas, minimo esperado {min_items}.",
        }
        if state["iteration_count"] >= state["max_iterations"]:
            state["acceptance_status"] = "rejected"
        return state

    if any(item["score"] < min_score for item in recommendations):
        state["acceptance_status"] = "retry"
        state["failure_diagnosis"] = {
            "iteration": state["iteration_count"],
            "reason": "Al menos una alternativa no cumple score minimo.",
        }
        if state["iteration_count"] >= state["max_iterations"]:
            state["acceptance_status"] = "rejected"
        return state

    state["acceptance_status"] = "approved"
    return state
