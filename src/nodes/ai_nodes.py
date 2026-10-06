from langchain_core.messages import SystemMessage, HumanMessage
from src.core.state import AgentState
from src.services.llm_service import llm_client

def gemini_enricher_node(state: AgentState) -> dict:
    """Nodo 4: Análisis semántico y decisión de Tool Calling."""
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
            f"PASO 4 (AI Router): Análisis completado. Herramienta solicitada: '{response.tool_name or 'Ninguna'}'"
        ]
    }

def incident_synthesizer_node(state: AgentState) -> dict:
    """
    Nodo 4.2: Agente Analista / Sintetizador.
    Consume la telemetría devuelta por la herramienta y genera el reporte técnico de incidente.
    """
    payload = state.get("tool_payload") or {}

    report = llm_client.generate_incident_report(payload)

    return {
        "incident_report": report,
        "audit_log": [
            f"PASO 4.2 (Synthesizer Agent): Reporte estructurado generado con Severidad: {report['calculated_severity']}."
        ]
    }