from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, TypedDict


class RecommendationState(TypedDict):
    original_criteria: Dict[str, Any]
    current_criteria: Dict[str, Any]
    zone_candidates: List[Dict[str, Any]]
    zone_evaluations: List[Dict[str, Any]]
    external_signals: List[Dict[str, Any]]
    property_results: List[Dict[str, Any]]
    filtered_properties: List[Dict[str, Any]]
    scored_alternatives: List[Dict[str, Any]]
    decision_history: List[Dict[str, Any]]
    relaxation_level: int
    relaxation_log: List[Dict[str, Any]]
    failure_diagnosis: Dict[str, Any]
    iteration_count: int
    max_iterations: int
    acceptance_status: Literal["pending", "approved", "retry", "rejected"]
    final_recommendations: List[Dict[str, Any]]


@dataclass(frozen=True)
class CriteriaDefaults:
    max_budget_cop: int = 320000000
    min_area_m2: int = 70
    property_type: str = "apartamento"
    min_safety: float = 0.6
    preferred_zones: Optional[List[str]] = None
    min_alternatives: int = 3
    min_score: float = 0.65


def create_initial_state(criteria: Dict[str, Any], max_iterations: int = 5) -> RecommendationState:
    defaults = CriteriaDefaults()
    merged_criteria = {
        "max_budget_cop": criteria.get("max_budget_cop", defaults.max_budget_cop),
        "min_area_m2": criteria.get("min_area_m2", defaults.min_area_m2),
        "property_type": criteria.get("property_type", defaults.property_type),
        "min_safety": criteria.get("min_safety", defaults.min_safety),
        "preferred_zones": criteria.get("preferred_zones", defaults.preferred_zones or []),
        "required_amenities": criteria.get("required_amenities", []),
        "min_alternatives": criteria.get("min_alternatives", defaults.min_alternatives),
        "min_score": criteria.get("min_score", defaults.min_score),
    }
    return RecommendationState(
        original_criteria=dict(merged_criteria),
        current_criteria=dict(merged_criteria),
        zone_candidates=[],
        zone_evaluations=[],
        external_signals=[],
        property_results=[],
        filtered_properties=[],
        scored_alternatives=[],
        decision_history=[],
        relaxation_level=0,
        relaxation_log=[],
        failure_diagnosis={},
        iteration_count=0,
        max_iterations=max_iterations,
        acceptance_status="pending",
        final_recommendations=[],
    )
