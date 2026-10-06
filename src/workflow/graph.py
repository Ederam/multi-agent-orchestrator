from langgraph.graph import StateGraph, START, END
from src.core.state import AgentState
from src.nodes.processing_nodes import (
    input_cleaner_node,
    validator_node,
    auto_fixer_node,
    final_processor_node,
)
from src.nodes.ai_nodes import gemini_enricher_node
from src.workflow.router import check_validation_route

def create_agent_graph():
    """Construye y compila el flujo del sistema multi-agente."""
    workflow = StateGraph(AgentState)

    # Registrar Nodos
    workflow.add_node("input_cleaner", input_cleaner_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("auto_fixer", auto_fixer_node)
    workflow.add_node("gemini_enricher", gemini_enricher_node)
    workflow.add_node("final_processor", final_processor_node)

    # Aristas fijas de inicio
    workflow.add_edge(START, "input_cleaner")
    workflow.add_edge("input_cleaner", "validator")

    # Arista condicional con ciclo de autocorrección
    workflow.add_conditional_edges(
        "validator",
        check_validation_route,
        {
            "gemini_enricher": "gemini_enricher",
            "auto_fixer": "auto_fixer",
            "fail_exit": END
        }
    )

    # Retorno del bucle de corrección al validador
    workflow.add_edge("auto_fixer", "validator")

    # Aristas finales
    workflow.add_edge("gemini_enricher", "final_processor")
    workflow.add_edge("final_processor", END)

    return workflow.compile()