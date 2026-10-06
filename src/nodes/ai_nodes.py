from langchain_core.messages import SystemMessage, HumanMessage
from src.core.state import AgentState
from src.services.llm_service import llm_client

def gemini_enricher_node(state: AgentState) -> dict:
    """Nodo encargado del análisis semántico y decisión de invocación de herramientas."""
    text_to_analyze = state["cleaned_data"]

    messages = [
        SystemMessage(content="Eres un Tech Lead de observabilidad. Evalúa la entrada y decide si requieres consultar métricas."),
        HumanMessage(content=text_to_analyze)
    ]

    response = llm_client.invoke(messages)

    return {
        "ai_analysis": response.content,
        "required_tool": response.tool_name,
        "audit_log": [
            f"PASO 4 (AI Node): Análisis completado. Herramienta solicitada: '{response.tool_name or 'Ninguna'}'"
        ]
    }