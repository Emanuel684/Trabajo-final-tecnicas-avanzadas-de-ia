from __future__ import annotations

from src.agents.utils import append_history, append_trace
from src.state import RecommendationState
from src.tools.housing_tools import attach_external_signals


def incorporate_external_signals(state: RecommendationState) -> RecommendationState:
    signals = attach_external_signals(state["zone_evaluations"])
    state["external_signals"] = signals
    append_trace(
        state,
        "signals_agent",
        "attach_urban_context",
        {
            "signal_count": len(signals),
            "headlines": {signal["zone"]: signal["headline"] for signal in signals},
        },
    )
    append_history(state, "incorporate_external_signals", signal_count=len(signals))
    return state
