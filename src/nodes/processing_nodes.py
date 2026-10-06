from src.core.state import AgentState
from src.services.tools import query_service_metrics

def input_cleaner_node(state: AgentState) -> dict:
    """Nodo 1: Sanea espacios y normaliza la entrada inicial."""
    raw_text = state["input_message"].strip()
    return {
        "cleaned_data": raw_text,
        "audit_log": [f"PASO 1 (Cleaner): Entrada normalizada -> '{raw_text}'"]
    }

def validator_node(state: AgentState) -> dict:
    """Nodo 2: Valida que la entrada cumpla con una longitud mínima de 10 caracteres."""
    current_text = state["cleaned_data"]
    attempts = state.get("retry_count", 0) + 1
    valid = len(current_text) >= 10

    return {
        "is_valid": valid,
        "retry_count": attempts,
        "audit_log": [f"PASO 2 (Validator - Intento {attempts}): Regla {'CUMPLIDA' if valid else 'INCUMPLIDA'}."]
    }

def auto_fixer_node(state: AgentState) -> dict:
    """Nodo 3: Aplica una corrección sintética para permitir que continúe el flujo."""
    fixed_text = state["cleaned_data"] + " [SOLICITUD_COMPLETA]"
    return {
        "cleaned_data": fixed_text,
        "audit_log": [f"PASO 3 (Auto-Fixer): Texto corregido -> '{fixed_text}'"]
    }

def tool_execution_node(state: AgentState) -> dict:
    """
    Nodo 4.1: Ejecutor de Herramientas (Tool Executor).
    Invoca query_service_metrics si el agente solicitó una herramienta.
    """
    tool_to_run = state.get("required_tool")
    target_text = state["cleaned_data"]

    if tool_to_run == "query_service_metrics":
        service_target = "pagos" if "pago" in target_text.lower() else "inventario"
        metrics = query_service_metrics(service_target)

        return {
            "tool_payload": metrics,
            "required_tool": None,
            "audit_log": [
                f"PASO 4.1 (Tool Node): Ejecutada 'query_service_metrics' para '{service_target}' -> Estado: {metrics['status']}, Latencia: {metrics['latency_ms']}ms."
            ]
        }

    return {
        "audit_log": ["PASO 4.1 (Tool Node): No se especificó ninguna herramienta válida."]
    }

def final_processor_node(state: AgentState) -> dict:
    """Nodo 5: Consolidador final del flujo."""
    return {
        "audit_log": ["PASO 5 (Final Processor): Pipeline finalizado. Estado consolidado."]
    }