from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.state import RecommendationState


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _read_json(filename: str) -> List[Dict[str, Any]]:
    with (DATA_DIR / filename).open("r", encoding="utf-8") as f:
        return json.load(f)


def interpret_requirements(state: RecommendationState) -> RecommendationState:
    state["decision_history"].append(
        {
            "stage": "interpret_requirements",
            "iteration": state["iteration_count"],
            "note": "Criterios de usuario normalizados y listos para evaluacion.",
        }
    )
    return state


def identify_zones(state: RecommendationState) -> RecommendationState:
    zones = _read_json("zones.json")
    criteria = state["current_criteria"]
    preferred = set(criteria.get("preferred_zones", []))
    min_safety = criteria["min_safety"]

    selected: List[Dict[str, Any]] = []
    for zone in zones:
        preferred_bonus = 0.1 if zone["name"] in preferred else 0.0
        if zone["safety_index"] + preferred_bonus >= min_safety:
            selected.append(zone)

    state["zone_candidates"] = selected
    state["decision_history"].append(
        {
            "stage": "identify_zones",
            "iteration": state["iteration_count"],
            "candidate_count": len(selected),
        }
    )
    return state


def evaluate_zones(state: RecommendationState) -> RecommendationState:
    evaluations: List[Dict[str, Any]] = []
    for zone in state["zone_candidates"]:
        transport = zone["transport_score"]
        services = zone["services_score"]
        safety = zone["safety_index"]
        quality_score = round((0.4 * safety) + (0.3 * transport) + (0.3 * services), 3)
        evaluations.append({"zone": zone["name"], "quality_score": quality_score, "raw_zone": zone})
    evaluations.sort(key=lambda item: item["quality_score"], reverse=True)
    state["zone_evaluations"] = evaluations
    return state


def inject_external_signals(state: RecommendationState) -> RecommendationState:
    signals = _read_json("signals.json")
    indexed = {s["zone"]: s for s in signals}
    attached: List[Dict[str, Any]] = []

    for evaluation in state["zone_evaluations"]:
        zone_name = evaluation["zone"]
        signal = indexed.get(zone_name, {"urban_context_score": 0.5, "headline": "Sin novedad"})
        attached.append(
            {
                "zone": zone_name,
                "urban_context_score": signal["urban_context_score"],
                "headline": signal["headline"],
            }
        )

    state["external_signals"] = attached
    return state


def search_properties(state: RecommendationState) -> RecommendationState:
    properties = _read_json("properties.json")
    valid_zones = {e["zone"] for e in state["zone_evaluations"]}
    state["property_results"] = [p for p in properties if p["zone"] in valid_zones]
    state["decision_history"].append(
        {
            "stage": "search_properties",
            "iteration": state["iteration_count"],
            "properties_found": len(state["property_results"]),
        }
    )
    return state


def filter_constraints(state: RecommendationState) -> RecommendationState:
    criteria = state["current_criteria"]
    required_amenities = set(criteria.get("required_amenities", []))
    filtered: List[Dict[str, Any]] = []

    for prop in state["property_results"]:
        if prop["price_cop"] > criteria["max_budget_cop"]:
            continue
        if prop["area_m2"] < criteria["min_area_m2"]:
            continue
        if prop["property_type"] != criteria["property_type"]:
            continue
        amenities = set(prop.get("amenities", []))
        if not required_amenities.issubset(amenities):
            continue
        filtered.append(prop)

    state["filtered_properties"] = filtered
    return state


def score_alternatives(state: RecommendationState) -> RecommendationState:
    zone_score = {z["zone"]: z["quality_score"] for z in state["zone_evaluations"]}
    signal_score = {s["zone"]: s["urban_context_score"] for s in state["external_signals"]}
    budget = state["current_criteria"]["max_budget_cop"]

    scored: List[Dict[str, Any]] = []
    for prop in state["filtered_properties"]:
        price_component = max(0.0, 1 - (prop["price_cop"] / max(budget * 1.2, 1)))
        area_component = min(1.0, prop["area_m2"] / max(state["current_criteria"]["min_area_m2"], 1))
        z_score = zone_score.get(prop["zone"], 0.5)
        u_score = signal_score.get(prop["zone"], 0.5)
        total = round((0.35 * z_score) + (0.25 * u_score) + (0.25 * price_component) + (0.15 * area_component), 3)

        scored.append(
            {
                **prop,
                "score": total,
                "explanation": (
                    f"Zona {prop['zone']} con calidad {z_score}, contexto urbano {u_score}, "
                    f"precio {prop['price_cop']} y area {prop['area_m2']}m2."
                ),
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    state["scored_alternatives"] = scored
    return state


def check_sufficiency(state: RecommendationState) -> RecommendationState:
    min_items = state["current_criteria"]["min_alternatives"]
    min_score = state["current_criteria"]["min_score"]
    accepted = [a for a in state["scored_alternatives"] if a["score"] >= min_score]
    state["final_recommendations"] = accepted[:min_items]
    state["decision_history"].append(
        {
            "stage": "check_sufficiency",
            "iteration": state["iteration_count"],
            "eligible_count": len(accepted),
            "required": min_items,
        }
    )
    return state


def diagnose_failure(state: RecommendationState) -> RecommendationState:
    reason = "No hay propiedades que cumplan los filtros actuales."
    if state["property_results"] and not state["filtered_properties"]:
        reason = "Se encontraron propiedades, pero ninguna cumple restricciones."
    elif state["filtered_properties"] and not state["final_recommendations"]:
        reason = "Hay opciones, pero no alcanzan el score minimo."

    state["failure_diagnosis"] = {
        "iteration": state["iteration_count"],
        "reason": reason,
        "budget": state["current_criteria"]["max_budget_cop"],
        "min_area_m2": state["current_criteria"]["min_area_m2"],
        "min_score": state["current_criteria"]["min_score"],
    }
    state["decision_history"].append({"stage": "diagnose_failure", **state["failure_diagnosis"]})
    return state


def explain_output(state: RecommendationState) -> RecommendationState:
    explained: List[Dict[str, Any]] = []
    for idx, item in enumerate(state["final_recommendations"], start=1):
        explained.append(
            {
                "rank": idx,
                "property_id": item["id"],
                "zone": item["zone"],
                "score": item["score"],
                "why": item["explanation"],
                "criteria_snapshot": dict(state["current_criteria"]),
            }
        )
    state["final_recommendations"] = explained
    state["decision_history"].append(
        {
            "stage": "explain_output",
            "iteration": state["iteration_count"],
            "output_count": len(explained),
            "acceptance_status": state["acceptance_status"],
        }
    )
    return state
