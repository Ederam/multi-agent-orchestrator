from langgraph.graph import StateGraph, START, END
from src.core.state import AgentState
from src.nodes.processing_nodes import (
    input_cleaner_node,
    validator_node,
    auto_fixer_node,
    tool_execution_node,
    final_processor_node,
)
from src.nodes.ai_nodes import (
    gemini_enricher_node,
    incident_synthesizer_node,
    notification_agent_node,
)
from src.workflow.router import check_validation_route, route_after_ai

def create_agent_graph():
    """Construye y compila el flujo completo del sistema multi-agente."""
    workflow = StateGraph(AgentState)

    # 1. Registrar Nodos
    workflow.add_node("input_cleaner", input_cleaner_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("auto_fixer", auto_fixer_node)
    workflow.add_node("gemini_enricher", gemini_enricher_node)
    workflow.add_node("tool_executor", tool_execution_node)
    workflow.add_node("incident_synthesizer", incident_synthesizer_node)
    workflow.add_node("notification_agent", notification_agent_node)
    workflow.add_node("final_processor", final_processor_node)

    # 2. Conectar Flujo Inicial y Autocorrección
    workflow.add_edge(START, "input_cleaner")
    workflow.add_edge("input_cleaner", "validator")

    workflow.add_conditional_edges(
        "validator",
        check_validation_route,
        {
            "gemini_enricher": "gemini_enricher",
            "auto_fixer": "auto_fixer",
            "fail_exit": END
        }
    )
    workflow.add_edge("auto_fixer", "validator")

    # 3. Decisión de Tool Calling
    workflow.add_conditional_edges(
        "gemini_enricher",
        route_after_ai,
        {
            "tool_executor": "tool_executor",
            "final_processor": "final_processor"
        }
    )

    # 4. Cadena Multi-Agente: Tool -> Sintetizador -> Notificador -> Cierre
    workflow.add_edge("tool_executor", "incident_synthesizer")
    workflow.add_edge("incident_synthesizer", "notification_agent")
    workflow.add_edge("notification_agent", "final_processor")
    workflow.add_edge("final_processor", END)

    return workflow.compile()