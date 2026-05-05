from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.graph import build_graph
from src.state import create_initial_state


def run_case(name: str, criteria: dict) -> None:
    print(f"\n===== {name} =====")
    app = build_graph()
    state = create_initial_state(criteria=criteria, max_iterations=7)
    result = app.invoke(state)

    print("Criterios originales:")
    print(json.dumps(result["original_criteria"], indent=2, ensure_ascii=False))
    print("Criterios finales:")
    print(json.dumps(result["current_criteria"], indent=2, ensure_ascii=False))
    print(f"Estatus de aceptacion: {result['acceptance_status']}")
    print(f"Iteraciones: {result['iteration_count']} / {result['max_iterations']}")
    print("Log de relajacion:")
    print(json.dumps(result["relaxation_log"], indent=2, ensure_ascii=False))
    print("Recomendaciones finales:")
    print(json.dumps(result["final_recommendations"], indent=2, ensure_ascii=False))


def main() -> None:
    strict_case = {
        "max_budget_cop": 300000000,
        "min_area_m2": 75,
        "property_type": "apartamento",
        "min_safety": 0.75,
        "preferred_zones": ["Laureles", "Envigado"],
        "required_amenities": ["parqueadero", "ascensor", "balcon"],
        "min_alternatives": 1,
        "min_score": 0.72,
    }

    relaxed_case = {
        "max_budget_cop": 290000000,
        "min_area_m2": 74,
        "property_type": "apartamento",
        "min_safety": 0.78,
        "preferred_zones": ["Envigado"],
        "required_amenities": ["parqueadero", "ascensor", "balcon"],
        "min_alternatives": 1,
        "min_score": 0.65,
    }

    run_case("Caso A (deberia converger rapido)", strict_case)
    run_case("Caso B (deberia requerir relajacion)", relaxed_case)


if __name__ == "__main__":
    main()
