from __future__ import annotations

from typing import Any, Dict, List, Tuple

from src.state import RecommendationState


def _append_relaxation(state: RecommendationState, field: str, old_value: Any, new_value: Any, reason: str) -> None:
    state["relaxation_log"].append(
        {
            "iteration": state["iteration_count"],
            "relaxation_level": state["relaxation_level"],
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason,
        }
    )


def relax_constraints(state: RecommendationState) -> RecommendationState:
    state["iteration_count"] += 1
    state["relaxation_level"] += 1
    criteria = state["current_criteria"]
    level = state["relaxation_level"]

    # A single primary variable is modified per iteration for interpretability.
    strategy: List[Tuple[str, str]] = [
        ("budget", "Aumentar presupuesto maximo +5%."),
        ("area", "Reducir area minima -5 m2."),
        ("score", "Reducir score minimo -0.05."),
        ("amenities", "Eliminar una amenidad obligatoria."),
        ("zones", "Permitir cualquier zona compatible por seguridad."),
        ("safety", "Reducir umbral de seguridad -0.03."),
    ]
    step = strategy[(level - 1) % len(strategy)][0]
    reason = strategy[(level - 1) % len(strategy)][1]

    if step == "budget":
        old = criteria["max_budget_cop"]
        new = int(old * 1.05)
        max_budget_limit = int(state["original_criteria"]["max_budget_cop"] * 1.30)
        criteria["max_budget_cop"] = min(new, max_budget_limit)
        _append_relaxation(state, "max_budget_cop", old, criteria["max_budget_cop"], reason)
    elif step == "area":
        old = criteria["min_area_m2"]
        criteria["min_area_m2"] = max(45, old - 5)
        _append_relaxation(state, "min_area_m2", old, criteria["min_area_m2"], reason)
    elif step == "score":
        old = criteria["min_score"]
        criteria["min_score"] = max(0.45, round(old - 0.05, 3))
        _append_relaxation(state, "min_score", old, criteria["min_score"], reason)
    elif step == "amenities":
        old = list(criteria.get("required_amenities", []))
        if old:
            new = old[:-1]
            criteria["required_amenities"] = new
            _append_relaxation(state, "required_amenities", old, new, reason)
        else:
            _append_relaxation(state, "required_amenities", old, old, "No habia amenidades que relajar.")
    else:
        if step == "zones":
            old = list(criteria.get("preferred_zones", []))
            criteria["preferred_zones"] = []
            _append_relaxation(state, "preferred_zones", old, [], reason)
        else:
            old = criteria["min_safety"]
            criteria["min_safety"] = max(0.60, round(old - 0.03, 3))
            _append_relaxation(state, "min_safety", old, criteria["min_safety"], reason)

    state["decision_history"].append(
        {
            "stage": "relax_constraints",
            "iteration": state["iteration_count"],
            "level": state["relaxation_level"],
            "step": step,
        }
    )
    return state
