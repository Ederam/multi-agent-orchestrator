from typing import Literal
from src.core.state import AgentState

def check_validation_route(state: AgentState) -> Literal["gemini_enricher", "auto_fixer", "fail_exit"]:
    """Determina si pasar al LLM, corregir o abortar según el estado."""
    if state["is_valid"]:
        return "gemini_enricher"
    
    if state["retry_count"] < 2:
        return "auto_fixer"
        
    return "fail_exit"