import os
from typing import Annotated, Literal, TypedDict, List
from dotenv import load_dotenv
import operator
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ---------------------------------------------------------------------------
# 1. Definición del Estado con Acumulador (Annotated + operator.add)
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    input_message: str
    cleaned_data: str
    audit_log: Annotated[List[str], operator.add]  # Acumula logs sin sobrescribir los anteriores
    retry_count: int
    is_valid: bool


# ---------------------------------------------------------------------------
# 2. Nodos de Procesamiento
# ---------------------------------------------------------------------------
def input_cleaner_node(state: AgentState) -> dict:
    """Nodo 1: Sanea la entrada y registra la acción en el log acumulativo."""
    raw_text = state["input_message"].strip()
    return {
        "cleaned_data": raw_text,
        "audit_log": [f"PASO 1: Entrada saneada -> '{raw_text}'"]
    }


def validator_node(state: AgentState) -> dict:
    """
    Nodo 2: Valida si los datos cumplen con la regla de negocio.
    Regla: El mensaje debe tener más de 10 caracteres.
    """
    current_text = state["cleaned_data"]
    attempts = state.get("retry_count", 0) + 1
    
    # Simulación de regla de validación
    valid = len(current_text) >= 10

    return {
        "is_valid": valid,
        "retry_count": attempts,
        "audit_log": [f"PASO 2 (Intento {attempts}): Validación {'EXITOSA' if valid else 'FALLIDA'}."]
    }


def auto_fixer_node(state: AgentState) -> dict:
    """Nodo 3: Intenta corregir el texto si la validación falló agregando padding."""
    fixed_text = state["cleaned_data"] + " [COMPLETADO]"
    return {
        "cleaned_data": fixed_text,
        "audit_log": [f"PASO 3: Corrección automática aplicada -> '{fixed_text}'"]
    }


def final_processor_node(state: AgentState) -> dict:
    """Nodo 4: Procesa el mensaje validado para su salida."""
    return {
        "audit_log": ["PASO 4: Procesamiento final completado con éxito."]
    }


# ---------------------------------------------------------------------------
# 3. Función del Router / Arista Condicional (Self-Correction Loop)
# ---------------------------------------------------------------------------
def check_validation_route(state: AgentState) -> Literal["final_processor", "auto_fixer", "fail_exit"]:
    """
    Evalúa el estado para decidir:
    - Si es válido -> Avanzar al procesador final.
    - Si es inválido y reintentos < 2 -> Ir al nodo de auto-corrección.
    - Si supera los reintentos -> Salir con fallo.
    """
    if state["is_valid"]:
        return "final_processor"
    
    if state["retry_count"] < 2:
        return "auto_fixer"
        
    return "fail_exit"


# ---------------------------------------------------------------------------
# 4. Ensamblado del Grafo
# ---------------------------------------------------------------------------
workflow = StateGraph(AgentState)

# Registrar Nodos
workflow.add_node("input_cleaner", input_cleaner_node)
workflow.add_node("validator", validator_node)
workflow.add_node("auto_fixer", auto_fixer_node)
workflow.add_node("final_processor", final_processor_node)

# Flujo Inicial
workflow.add_edge(START, "input_cleaner")
workflow.add_edge("input_cleaner", "validator")

# Arista Condicional con Bucle de Auto-Corrección
workflow.add_conditional_edges(
    "validator",
    check_validation_route,
    {
        "final_processor": "final_processor",
        "auto_fixer": "auto_fixer",
        "fail_exit": END
    }
)

# Arista de retorno desde el fixer hacia la re-validación (Ciclo/Bucle)
workflow.add_edge("auto_fixer", "validator")

# Salida del procesador final
workflow.add_edge("final_processor", END)

app = workflow.compile()


# ---------------------------------------------------------------------------
# 5. Ejecución y Pruebas
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n==================================================")
    print("      PRUEBA 1: Entrada Válida desde el Inicio")
    print("==================================================")
    state_valid: AgentState = {
        "input_message": "  Mensaje largo de prueba que pasa directo  ",
        "cleaned_data": "",
        "audit_log": [],
        "retry_count": 0,
        "is_valid": False
    }
    result_1 = app.invoke(state_valid)
    for log in result_1["audit_log"]:
        print(f"  -> {log}")

    print("\n==================================================")
    print("      PRUEBA 2: Entrada Corta (Activa Bucle de Corrección)")
    print("==================================================")
    state_short: AgentState = {
        "input_message": "  Hola  ",
        "cleaned_data": "",
        "audit_log": [],
        "retry_count": 0,
        "is_valid": False
    }
    result_2 = app.invoke(state_short)
    for log in result_2["audit_log"]:
        print(f"  -> {log}")
    print("==================================================\n")