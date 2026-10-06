from src.core.config import settings

class LLMToolResponse:
    def __init__(self, content: str, tool_name: str | None = None):
        self.content = content
        self.tool_name = tool_name

class MockLLMClient:
    """
    Cliente Sandbox Seguro con soporte para Tool Calling determinista.
    """
    def __init__(self, model: str = "sandbox-agent"):
        self.model = model

    def invoke(self, messages: list) -> LLMToolResponse:
        user_text = ""
        for msg in messages:
            if hasattr(msg, "content"):
                user_text += f" {msg.content}"
            elif isinstance(msg, dict):
                user_text += f" {msg.get('content', '')}"

        user_text_lower = user_text.lower()

        # Decisión autónoma del agente: ¿necesito una herramienta?
        if "pago" in user_text_lower:
            return LLMToolResponse(
                content="Detecto un posible incidente en el subsistema de pagos. Solicitando telemetría de red...",
                tool_name="query_service_metrics"
            )
        elif "inventario" in user_text_lower:
            return LLMToolResponse(
                content="Detecto consulta sobre el subsistema de inventario. Solicitando métricas operativas...",
                tool_name="query_service_metrics"
            )
        else:
            return LLMToolResponse(
                content=f"Consulta general analizada sin requerimiento de herramientas: '{user_text.strip()}'.",
                tool_name=None
            )

def get_gemini_client():
    return MockLLMClient(model=settings.MODEL_NAME)

llm_client = get_gemini_client()