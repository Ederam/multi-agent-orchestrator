from langchain_core.messages import SystemMessage, HumanMessage
from src.core.state import AgentState
from src.services.llm_service import llm_client

def gemini_enricher_node(state: AgentState) -> dict:
    """Nodo encargado del análisis semántico mediante Gemini."""
    text_to_analyze = state["cleaned_data"]

    if not llm_client:
        fallback_msg = "[MODO OFFLINE]: No se detectó GEMINI_API_KEY en .env. Consumo simulado."
        return {
            "ai_analysis": fallback_msg,
            "audit_log": [f"PASO 4 (Gemini Node): {fallback_msg}"]
        }

    try:
        messages = [
            SystemMessage(content="Eres un analista de software backend. Clasifica la intención y resume en una frase concisa."),
            HumanMessage(content=text_to_analyze)
        ]
        
        response = llm_client.invoke(messages)
        ai_result = str(response.content).strip()

        return {
            "ai_analysis": ai_result,
            "audit_log": ["PASO 4 (Gemini Node): Análisis recibido de Gemini 2.5 Flash exitosamente."]
        }
    except Exception as ex:
        error_msg = f"[ERROR CONSUMO GEMINI]: {str(ex)}"
        return {
            "ai_analysis": error_msg,
            "audit_log": [f"PASO 4 (Gemini Node Fallo): {error_msg}"]
        }