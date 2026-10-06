from src.core.config import settings

class LLMToolResponse:
    def __init__(self, content: str, tool_name: str | None = None):
        self.content = content
        self.tool_name = tool_name

class MockLLMClient:
    """
    Cliente Sandbox Seguro con capacidades de análisis semántico y síntesis estructurada.
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

        # Decisión de invocación de herramientas
        if "pago" in user_text_lower:
            return LLMToolResponse(
                content="Incidente potencial detectado en microservicio de pagos. Solicitando telemetría...",
                tool_name="query_service_metrics"
            )
        elif "inventario" in user_text_lower:
            return LLMToolResponse(
                content="Consulta de inventario detectada. Solicitando métricas operativas...",
                tool_name="query_service_metrics"
            )
        else:
            return LLMToolResponse(
                content=f"Consulta procesada sin requerimiento de herramientas: '{user_text.strip()}'.",
                tool_name=None
            )

    def generate_incident_report(self, payload: dict) -> dict:
        """
        Sintetizador: Procesa métricas crudas de infraestructura y genera
        un informe de diagnóstico estructurado.
        """
        service = payload.get("service", "Desconocido")
        status = payload.get("status", "UNKNOWN")
        latency = payload.get("latency_ms", 0)
        error_rate = payload.get("error_rate_pct", 0.0)

        # Regla de cálculo de severidad
        if status == "DEGRADED" or error_rate > 20.0 or latency > 3000:
            severity = "P1 - CRÍTICA"
            impact = "Afectación directa en transacciones financieras de clientes."
            recommendation = "Activar failover hacia pasarela secundaria y reiniciar pods degradados."
        else:
            severity = "P3 - MENOR"
            impact = "Operación nominal o degradación leve sin afectación perceptible."
            recommendation = "Monitoreo continuo de dashboards sin intervención manual."

        return {
            "service_name": service,
            "status": status,
            "calculated_severity": severity,
            "latency_observed": f"{latency} ms",
            "error_rate": f"{error_rate} %",
            "business_impact": impact,
            "recommended_action": recommendation
        }

def get_gemini_client():
    return MockLLMClient(model=settings.MODEL_NAME)

llm_client = get_gemini_client()