import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

# Cargar variables de entorno del archivo .env
load_dotenv()


# ---------------------------------------------------------------------------
# 1. State Definition (DTO Inmutable que fluye a través del Grafo)
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    input_message: str
    processed_message: str
    step_count: int


# ---------------------------------------------------------------------------
# 2. Node Implementations (Servicios/Funciones puras de transformación)
# ---------------------------------------------------------------------------
def normalizer_node(state: AgentState) -> dict:
    """Nodo 1: Limpia y estandariza la entrada del usuario."""
    raw_text = state["input_message"].strip().upper()
    return {
        "processed_message": f"[NORMALIZED]: {raw_text}",
        "step_count": state.get("step_count", 0) + 1,
    }


def enricher_node(state: AgentState) -> dict:
    """Nodo 2: Enriquece el estado agregando metadatos de ejecución."""
    current_text = state["processed_message"]
    return {
        "processed_message": f"{current_text} | Processed by Graph Engine v1.0",
        "step_count": state["step_count"] + 1,
    }


# ---------------------------------------------------------------------------
# 3. Graph Assembly (Orquestador)
# ---------------------------------------------------------------------------
workflow = StateGraph(AgentState)

# Registrar Nodos
workflow.add_node("normalizer", normalizer_node)
workflow.add_node("enricher", enricher_node)

# Definir Aristas (Edges) - Flujo secuencial
workflow.add_edge(START, "normalizer")
workflow.add_edge("normalizer", "enricher")
workflow.add_edge("enricher", END)

# Compilar la aplicación ejecutable
app = workflow.compile()


# ---------------------------------------------------------------------------
# 4. Entry Point / Execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    initial_state: AgentState = {
        "input_message": "  hola agente desde langgraph   ",
        "processed_message": "",
        "step_count": 0,
    }

    # Invocación sincrónica del grafo
    final_state = app.invoke(initial_state)

    print("\n==================================================")
    print("      EJECUCIÓN DEL GRAFO DE ESTADO EXITOSA       ")
    print("==================================================")
    print(f"Input Inicial  : '{initial_state['input_message']}'")
    print(f"Output Final   : '{final_state['processed_message']}'")
    print(f"Pasos Totales  : {final_state['step_count']}\n")