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
    """Evalúa si la IA solicitó una herramienta o si concluye directamente."""
    if state.get("required_tool"):
        return "tool_executor"
    return "final_processor"

def route_after_human_review(state: AgentState) -> Literal["notification_agent", "final_processor"]:
    """
    Evalúa la decisión humana:
    - Si el humano aprobó (True) -> Pasa al agente notificador.
    - Si rechazó (False) -> Salta el despacho y va directo al cierre.
    """
    if state.get("human_approved") is True:
        return "notification_agent"
    return "final_processor"