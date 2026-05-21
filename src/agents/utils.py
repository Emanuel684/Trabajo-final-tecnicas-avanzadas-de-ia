from __future__ import annotations

from typing import Any, Dict

from src.state import RecommendationState


def append_history(state: RecommendationState, stage: str, **payload: Any) -> None:
    state["decision_history"].append(
        {
            "stage": stage,
            "iteration": state["iteration_count"],
            **payload,
        }
    )


def append_trace(
    state: RecommendationState,
    agent: str,
    action: str,
    output: Dict[str, Any],
    mode: str = "deterministic",
) -> None:
    state["agent_traces"].append(
        {
            "agent": agent,
            "iteration": state["iteration_count"],
            "mode": mode,
            "action": action,
            "output": output,
        }
    )
