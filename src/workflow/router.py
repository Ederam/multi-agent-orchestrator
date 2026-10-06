from typing import Literal
from src.core.state import AgentState

def check_validation_route(state: AgentState) -> Literal["gemini_enricher", "auto_fixer", "fail_exit"]:
    """Determina si pasar al nodo de IA, corregir texto o abortar."""
    if state["is_valid"]:
        return "gemini_enricher"
    if state["retry_count"] < 2:
        return "auto_fixer"
    return "fail_exit"

def route_after_ai(state: AgentState) -> Literal["tool_executor", "final_processor"]:
    """
    Evalúa si la IA solicitó una herramienta o si se concluye directamente.
    """
    if state.get("required_tool"):
        return "tool_executor"
    return "final_processor"