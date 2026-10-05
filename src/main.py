import os
from typing import Literal, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ---------------------------------------------------------------------------
# 1. State Definition
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    input_message: str
    category: str  # "TECH", "GENERAL", o "UNKNOWN"
    processed_message: str
    step_count: int


# ---------------------------------------------------------------------------
# 2. Node Implementations
# ---------------------------------------------------------------------------
def classifier_node(state: AgentState) -> dict:
    """Nodo 1: Analiza el mensaje y determina la categoría."""
    text = state["input_message"].lower()
    
    if any(keyword in text for keyword in ["error", "bug", "python", "code", "database"]):
        detected_category = "TECH"
    else:
        detected_category = "GENERAL"

    return {
        "category": detected_category,
        "step_count": state.get("step_count", 0) + 1
    }


def tech_support_node(state: AgentState) -> dict:
    """Nodo 2A: Especializado en problemas técnicos."""
    return {
        "processed_message": f"[SOPORTE TÉCNICO]: Se ha registrado el ticket técnico para '{state['input_message']}'.",
        "step_count": state["step_count"] + 1
    }


def general_info_node(state: AgentState) -> dict:
    """Nodo 2B: Especializado en consultas generales."""
    return {
        "processed_message": f"[ATENCIÓN GENERAL]: Respuesta general para '{state['input_message']}'.",
        "step_count": state["step_count"] + 1
    }


# ---------------------------------------------------------------------------
# 3. Router Function (Lógica para la Arista Condicional)
# ---------------------------------------------------------------------------
def route_by_category(state: AgentState) -> Literal["tech_support", "general_info"]:
    """
    Función de decisión pura: Lee el estado y retorna el NOMBRE EXACTO
    del nodo hacia el cual debe dirigirse el flujo.
    """
    if state["category"] == "TECH":
        return "tech_support"
    return "general_info"


# ---------------------------------------------------------------------------
# 4. Graph Assembly
# ---------------------------------------------------------------------------
workflow = StateGraph(AgentState)

# Registrar Nodos
workflow.add_node("classifier", classifier_node)
workflow.add_node("tech_support", tech_support_node)
workflow.add_node("general_info", general_info_node)

# Flujo Inicial
workflow.add_edge(START, "classifier")

# ARISTA CONDICIONAL:
# Del nodo 'classifier', evaluamos con 'route_by_category' a qué nodo ir.
workflow.add_conditional_edges(
    "classifier",
    route_by_category,
    {
        "tech_support": "tech_support",
        "general_info": "general_info"
    }
)

# Cierre de flujos hacia el final
workflow.add_edge("tech_support", END)
workflow.add_edge("general_info", END)

app = workflow.compile()


# ---------------------------------------------------------------------------
# 5. Execution Test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Prueba 1: Mensaje Técnico
    tech_input: AgentState = {
        "input_message": "Tengo un bug en el código de Python con la database",
        "category": "",
        "processed_message": "",
        "step_count": 0
    }

    result_tech = app.invoke(tech_input)

    print("\n--- PRUEBA 1 (Caso Técnico) ---")
    print(f"Input     : {tech_input['input_message']}")
    print(f"Categoría : {result_tech['category']}")
    print(f"Resultado : {result_tech['processed_message']}")
    print(f"Pasos     : {result_tech['step_count']}")

    # Prueba 2: Mensaje General
    general_input: AgentState = {
        "input_message": "Hola, ¿cuál es el horario de atención?",
        "category": "",
        "processed_message": "",
        "step_count": 0
    }

    result_general = app.invoke(general_input)

    print("\n--- PRUEBA 2 (Caso General) ---")
    print(f"Input     : {general_input['input_message']}")
    print(f"Categoría : {result_general['category']}")
    print(f"Resultado : {result_general['processed_message']}")
    print(f"Pasos     : {result_general['step_count']}\n")