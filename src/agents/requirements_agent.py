from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple

from src.agents.utils import append_history, append_trace
from src.state import RecommendationState, default_criteria
from src.tools.housing_tools import infer_criteria_from_text


def _load_openai_model() -> Optional[Any]:
    try:
        from dotenv import load_dotenv
        from langchain_openai import ChatOpenAI
    except ImportError:
        return None

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        return None
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


def _parse_with_llm(user_input: str) -> Optional[Tuple[Dict[str, Any], float]]:
    model = _load_openai_model()
    if model is None:
        return None

    schema = {
        "max_budget_cop": "integer or null",
        "min_area_m2": "integer or null",
        "property_type": "apartamento, casa, or null",
        "min_safety": "float from 0 to 1 or null",
        "preferred_zones": "array of zone names or empty array",
        "required_amenities": "array using parqueadero, ascensor, balcon",
        "min_alternatives": "integer or null",
        "min_score": "float from 0 to 1 or null",
        "family_size": "integer or null",
        "confidence": "float from 0 to 1",
    }
    prompt = (
        "Extrae criterios de busqueda de vivienda desde el texto del usuario. "
        "Devuelve solo JSON valido con las claves de este esquema: "
        f"{json.dumps(schema, ensure_ascii=False)}. "
        "No inventes datos ausentes; usa null o arrays vacios.\n\n"
        f"Texto: {user_input}"
    )
    response = model.invoke(prompt)
    try:
        payload = json.loads(response.content)
    except (json.JSONDecodeError, TypeError, AttributeError):
        return None

    confidence = float(payload.pop("confidence", 0.75))
    criteria = default_criteria(payload)
    return criteria, round(max(0.0, min(confidence, 1.0)), 2)


def interpret_requirements(state: RecommendationState) -> RecommendationState:
    llm_result = _parse_with_llm(state["raw_user_input"])
    mode = "llm" if llm_result else "heuristic"

    if llm_result:
        criteria, confidence = llm_result
        evidence = ["llm_structured_extraction"]
    else:
        criteria, confidence, evidence = infer_criteria_from_text(state["raw_user_input"])

    state["original_criteria"] = dict(criteria)
    state["current_criteria"] = dict(criteria)
    state["criteria_confidence"] = confidence

    append_trace(
        state,
        "requirements_agent",
        "parse_user_text",
        {
            "criteria": criteria,
            "confidence": confidence,
            "evidence": evidence,
        },
        mode=mode,
    )
    append_history(
        state,
        "interpret_requirements",
        note="Texto de usuario convertido a criterios estructurados.",
        confidence=confidence,
    )
    return state
