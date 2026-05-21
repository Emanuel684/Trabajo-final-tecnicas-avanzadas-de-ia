from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.graph import build_graph
from src.state import create_initial_state


def run_case(name: str, user_input: str, max_iterations: int = 6) -> None:
    print(f"\n===== {name} =====")
    print(f"Entrada del usuario: {user_input}")

    app = build_graph()
    initial_state = create_initial_state(user_input=user_input, max_iterations=max_iterations)
    result = app.invoke(initial_state)

    print("\nCriterios interpretados:")
    print(json.dumps(result["original_criteria"], indent=2, ensure_ascii=False))
    print("\nCriterios finales:")
    print(json.dumps(result["current_criteria"], indent=2, ensure_ascii=False))
    print(f"\nEstado de aceptacion: {result['acceptance_status']}")
    print(f"Iteraciones: {result['iteration_count']} / {result['max_iterations']}")
    print("\nRelajaciones aplicadas:")
    print(json.dumps(result["relaxation_log"], indent=2, ensure_ascii=False))
    print("\nRecomendaciones finales:")
    print(json.dumps(result["final_recommendations"], indent=2, ensure_ascii=False))
    print("\nUltimas decisiones:")
    print(json.dumps(result["decision_history"][-6:], indent=2, ensure_ascii=False))


def main() -> None:
    run_case(
        "Caso A - texto libre con solucion directa",
        (
            "Somos una familia de 4 personas. Queremos un apartamento seguro en "
            "Laureles o Envigado, con parqueadero y ascensor, maximo 360 millones, "
            "al menos 70 m2 y dos opciones."
        ),
    )
    run_case(
        "Caso B - requiere relajacion progresiva",
        (
            "Busco apartamento muy seguro en Envigado, con parqueadero, ascensor y "
            "balcon, maximo 300 millones, minimo 80 m2 y dos opciones."
        ),
    )


if __name__ == "__main__":
    main()
