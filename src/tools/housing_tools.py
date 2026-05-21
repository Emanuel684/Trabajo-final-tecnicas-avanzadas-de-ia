from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Tuple

from src.state import default_criteria


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def read_json(filename: str) -> List[Dict[str, Any]]:
    with (DATA_DIR / filename).open("r", encoding="utf-8") as file:
        return json.load(file)


def load_zones() -> List[Dict[str, Any]]:
    return read_json("zones.json")


def load_properties() -> List[Dict[str, Any]]:
    return read_json("properties.json")


def load_signals() -> List[Dict[str, Any]]:
    return read_json("signals.json")


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def infer_criteria_from_text(user_input: str) -> Tuple[Dict[str, Any], float, List[str]]:
    text = normalize_text(user_input)
    criteria = default_criteria()
    evidence: List[str] = []

    budget_match = re.search(r"(\d+(?:[\.,]\d+)?)\s*(millones|millon)", text)
    if budget_match:
        amount = float(budget_match.group(1).replace(",", "."))
        criteria["max_budget_cop"] = int(amount * 1_000_000)
        evidence.append("budget")
    else:
        cop_match = re.search(r"(\d{7,10})", text.replace(".", "").replace(",", ""))
        if cop_match:
            criteria["max_budget_cop"] = int(cop_match.group(1))
            evidence.append("budget")

    area_match = re.search(r"(\d{2,3})\s*(m2|metros|metro)", text)
    if area_match:
        criteria["min_area_m2"] = int(area_match.group(1))
        evidence.append("area")

    family_match = re.search(r"familia\s+de\s+(\d+)|(\d+)\s+personas", text)
    if family_match:
        criteria["family_size"] = int(next(group for group in family_match.groups() if group))
        evidence.append("family_size")

    if "casa" in text:
        criteria["property_type"] = "casa"
        evidence.append("property_type")
    elif "apartamento" in text or "apto" in text:
        criteria["property_type"] = "apartamento"
        evidence.append("property_type")

    preferred_zones = []
    for zone in load_zones():
        if normalize_text(zone["name"]) in text:
            preferred_zones.append(zone["name"])
    if preferred_zones:
        criteria["preferred_zones"] = preferred_zones
        evidence.append("preferred_zones")

    amenities = {
        "parqueadero": ["parqueadero", "garage", "garaje"],
        "ascensor": ["ascensor"],
        "balcon": ["balcon", "balcon"],
    }
    required_amenities = []
    for amenity, aliases in amenities.items():
        if any(alias in text for alias in aliases):
            required_amenities.append(amenity)
    if required_amenities:
        criteria["required_amenities"] = required_amenities
        evidence.append("required_amenities")

    if "seguro" in text or "seguridad" in text:
        criteria["min_safety"] = max(criteria["min_safety"], 0.75)
        evidence.append("safety")

    if "2 opciones" in text or "dos opciones" in text:
        criteria["min_alternatives"] = 2
        evidence.append("min_alternatives")
    elif "1 opcion" in text or "una opcion" in text:
        criteria["min_alternatives"] = 1
        evidence.append("min_alternatives")

    confidence = min(1.0, 0.25 + (0.10 * len(set(evidence))))
    return criteria, round(confidence, 2), evidence


def identify_zone_candidates(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    zones = load_zones()
    preferred = set(criteria.get("preferred_zones", []))
    min_safety = criteria["min_safety"]
    selected: List[Dict[str, Any]] = []

    for zone in zones:
        is_preferred = zone["name"] in preferred
        if preferred and not is_preferred:
            continue
        preferred_bonus = 0.1 if is_preferred else 0.0
        if zone["safety_index"] + preferred_bonus >= min_safety:
            selected.append(zone)

    return selected


def evaluate_zone_candidates(zones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    evaluations: List[Dict[str, Any]] = []
    for zone in zones:
        quality_score = round(
            (0.4 * zone["safety_index"])
            + (0.3 * zone["transport_score"])
            + (0.3 * zone["services_score"]),
            3,
        )
        evaluations.append(
            {
                "zone": zone["name"],
                "quality_score": quality_score,
                "raw_zone": zone,
            }
        )
    evaluations.sort(key=lambda item: item["quality_score"], reverse=True)
    return evaluations


def attach_external_signals(zone_evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    indexed_signals = {signal["zone"]: signal for signal in load_signals()}
    attached: List[Dict[str, Any]] = []

    for evaluation in zone_evaluations:
        zone_name = evaluation["zone"]
        signal = indexed_signals.get(
            zone_name,
            {"urban_context_score": 0.5, "headline": "Sin novedad registrada."},
        )
        attached.append(
            {
                "zone": zone_name,
                "urban_context_score": signal["urban_context_score"],
                "headline": signal["headline"],
            }
        )
    return attached


def search_properties_for_zones(zone_evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    valid_zones = {evaluation["zone"] for evaluation in zone_evaluations}
    return [prop for prop in load_properties() if prop["zone"] in valid_zones]


def filter_properties(
    properties: List[Dict[str, Any]],
    criteria: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    required_amenities = set(criteria.get("required_amenities", []))
    rejection_counts = {
        "budget": 0,
        "area": 0,
        "property_type": 0,
        "amenities": 0,
    }
    filtered: List[Dict[str, Any]] = []

    for prop in properties:
        if prop["price_cop"] > criteria["max_budget_cop"]:
            rejection_counts["budget"] += 1
            continue
        if prop["area_m2"] < criteria["min_area_m2"]:
            rejection_counts["area"] += 1
            continue
        if prop["property_type"] != criteria["property_type"]:
            rejection_counts["property_type"] += 1
            continue
        amenities = set(prop.get("amenities", []))
        if not required_amenities.issubset(amenities):
            rejection_counts["amenities"] += 1
            continue
        filtered.append(prop)

    return filtered, rejection_counts


def score_properties(
    properties: List[Dict[str, Any]],
    zone_evaluations: List[Dict[str, Any]],
    external_signals: List[Dict[str, Any]],
    criteria: Dict[str, Any],
) -> List[Dict[str, Any]]:
    zone_score = {zone["zone"]: zone["quality_score"] for zone in zone_evaluations}
    signal_score = {signal["zone"]: signal["urban_context_score"] for signal in external_signals}
    budget = max(criteria["max_budget_cop"], 1)
    min_area = max(criteria["min_area_m2"], 1)
    scored: List[Dict[str, Any]] = []

    for prop in properties:
        price_component = max(0.0, 1 - (prop["price_cop"] / (budget * 1.2)))
        area_component = min(1.0, prop["area_m2"] / min_area)
        z_score = zone_score.get(prop["zone"], 0.5)
        u_score = signal_score.get(prop["zone"], 0.5)
        total = round(
            (0.35 * z_score)
            + (0.25 * u_score)
            + (0.25 * price_component)
            + (0.15 * area_component),
            3,
        )

        scored.append(
            {
                **prop,
                "score": total,
                "score_breakdown": {
                    "zone": z_score,
                    "urban_context": u_score,
                    "price": round(price_component, 3),
                    "area": round(area_component, 3),
                },
                "explanation": (
                    f"Zona {prop['zone']} con calidad {z_score}, contexto urbano {u_score}, "
                    f"precio {prop['price_cop']} COP y area {prop['area_m2']} m2."
                ),
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored


def select_accepted_alternatives(
    scored_alternatives: List[Dict[str, Any]],
    criteria: Dict[str, Any],
) -> List[Dict[str, Any]]:
    accepted = [
        alternative
        for alternative in scored_alternatives
        if alternative["score"] >= criteria["min_score"]
    ]
    return accepted[: criteria["min_alternatives"]]


def diagnose_failure(
    criteria: Dict[str, Any],
    zone_candidates: List[Dict[str, Any]],
    property_results: List[Dict[str, Any]],
    filtered_properties: List[Dict[str, Any]],
    scored_alternatives: List[Dict[str, Any]],
    rejection_counts: Dict[str, int],
    iteration: int,
) -> Dict[str, Any]:
    reason = "No hay propiedades que cumplan los filtros actuales."
    if not zone_candidates:
        reason = "Ninguna zona cumple la combinacion de preferencia y seguridad."
    elif property_results and not filtered_properties:
        dominant = max(rejection_counts, key=rejection_counts.get)
        reason = f"Hay propiedades en zonas viables, pero fallan principalmente por {dominant}."
    elif filtered_properties and not scored_alternatives:
        reason = "Hay propiedades filtradas, pero no se pudieron puntuar."
    elif scored_alternatives:
        reason = "Hay opciones, pero no alcanzan el score minimo o la cantidad requerida."

    return {
        "iteration": iteration,
        "reason": reason,
        "criteria_snapshot": dict(criteria),
        "rejection_counts": dict(rejection_counts),
    }


def apply_relaxation(
    criteria: Dict[str, Any],
    original_criteria: Dict[str, Any],
    iteration: int,
    relaxation_level: int,
    failure_diagnosis: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    updated = dict(criteria)
    strategy: List[Tuple[str, str]] = [
        ("max_budget_cop", "Aumentar presupuesto maximo en 5%."),
        ("min_area_m2", "Reducir area minima en 5 m2."),
        ("min_score", "Reducir score minimo en 0.05."),
        ("required_amenities", "Eliminar la ultima amenidad obligatoria."),
        ("preferred_zones", "Permitir otras zonas compatibles."),
        ("min_safety", "Reducir umbral de seguridad en 0.03."),
    ]
    field, reason = strategy[(relaxation_level - 1) % len(strategy)]
    old_value = updated.get(field)

    if field == "max_budget_cop":
        limit = int(original_criteria["max_budget_cop"] * 1.30)
        updated[field] = min(int(updated[field] * 1.05), limit)
    elif field == "min_area_m2":
        updated[field] = max(45, updated[field] - 5)
    elif field == "min_score":
        updated[field] = max(0.45, round(updated[field] - 0.05, 3))
    elif field == "required_amenities":
        current = list(updated.get(field, []))
        updated[field] = current[:-1] if current else current
    elif field == "preferred_zones":
        updated[field] = []
    elif field == "min_safety":
        updated[field] = max(0.60, round(updated[field] - 0.03, 3))

    entry = {
        "iteration": iteration,
        "relaxation_level": relaxation_level,
        "field": field,
        "old_value": old_value,
        "new_value": updated.get(field),
        "reason": reason,
        "failure_reason": failure_diagnosis.get("reason", "Sin diagnostico previo."),
    }
    return updated, entry
