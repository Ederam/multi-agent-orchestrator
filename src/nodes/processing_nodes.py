from src.core.state import AgentState

def input_cleaner_node(state: AgentState) -> dict:
    """Sanea espacios y normaliza la entrada inicial."""
    raw_text = state["input_message"].strip()
    return {
        "cleaned_data": raw_text,
        "audit_log": [f"PASO 1 (Cleaner): Entrada normalizada -> '{raw_text}'"]
    }

def validator_node(state: AgentState) -> dict:
    """Valida que la entrada cumpla con una longitud mínima de 10 caracteres."""
    current_text = state["cleaned_data"]
    attempts = state.get("retry_count", 0) + 1
    valid = len(current_text) >= 10

    return {
        "is_valid": valid,
        "retry_count": attempts,
        "audit_log": [f"PASO 2 (Validator - Intento {attempts}): Regla {'CUMPLIDA' if valid else 'INCUMPLIDA'}."]
    }

def auto_fixer_node(state: AgentState) -> dict:
    """Aplica una corrección sintética para permitir que continúe el flujo."""
    fixed_text = state["cleaned_data"] + " [SOLICITUD_COMPLETA]"
    return {
        "cleaned_data": fixed_text,
        "audit_log": [f"PASO 3 (Auto-Fixer): Texto corregido -> '{fixed_text}'"]
    }

def final_processor_node(state: AgentState) -> dict:
    """Consolidador final del flujo."""
    return {
        "audit_log": ["PASO 5 (Final Processor): Pipeline finalizado. Estado consolidado."]
    }