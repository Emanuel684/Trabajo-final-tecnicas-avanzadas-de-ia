from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, TypedDict


AcceptanceStatus = Literal["pending", "approved", "retry", "rejected"]


class RecommendationState(TypedDict):
    raw_user_input: str
    original_criteria: Dict[str, Any]
    current_criteria: Dict[str, Any]
    criteria_confidence: float
    zone_candidates: List[Dict[str, Any]]
    zone_evaluations: List[Dict[str, Any]]
    external_signals: List[Dict[str, Any]]
    property_results: List[Dict[str, Any]]
    filtered_properties: List[Dict[str, Any]]
    scored_alternatives: List[Dict[str, Any]]
    final_recommendations: List[Dict[str, Any]]
    decision_history: List[Dict[str, Any]]
    agent_traces: List[Dict[str, Any]]
    relaxation_level: int
    relaxation_log: List[Dict[str, Any]]
    failure_diagnosis: Dict[str, Any]
    iteration_count: int
    max_iterations: int
    acceptance_status: AcceptanceStatus
    sufficiency_status: Dict[str, Any]


@dataclass(frozen=True)
class CriteriaDefaults:
    max_budget_cop: int = 320000000
    min_area_m2: int = 70
    property_type: str = "apartamento"
    min_safety: float = 0.70
    min_alternatives: int = 3
    min_score: float = 0.65


def default_criteria(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    defaults = CriteriaDefaults()
    criteria: Dict[str, Any] = {
        "max_budget_cop": defaults.max_budget_cop,
        "min_area_m2": defaults.min_area_m2,
        "property_type": defaults.property_type,
        "min_safety": defaults.min_safety,
        "preferred_zones": [],
        "required_amenities": [],
        "min_alternatives": defaults.min_alternatives,
        "min_score": defaults.min_score,
        "family_size": None,
    }
    if overrides:
        criteria.update({key: value for key, value in overrides.items() if value is not None})
    return criteria


def create_initial_state(
    user_input: str,
    max_iterations: int = 6,
    criteria_overrides: Optional[Dict[str, Any]] = None,
) -> RecommendationState:
    criteria = default_criteria(criteria_overrides)
    return RecommendationState(
        raw_user_input=user_input,
        original_criteria=dict(criteria),
        current_criteria=dict(criteria),
        criteria_confidence=0.0,
        zone_candidates=[],
        zone_evaluations=[],
        external_signals=[],
        property_results=[],
        filtered_properties=[],
        scored_alternatives=[],
        final_recommendations=[],
        decision_history=[],
        agent_traces=[],
        relaxation_level=0,
        relaxation_log=[],
        failure_diagnosis={},
        iteration_count=0,
        max_iterations=max_iterations,
        acceptance_status="pending",
        sufficiency_status={},
    )
