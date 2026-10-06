from src.services.tools import query_service_metrics

def tool_execution_node(state: AgentState) -> dict:
    """
    Nodo Operativo (Tool Executor):
    Ejecuta la herramienta solicitada por el agente utilizando los datos del estado.
    """
    tool_to_run = state.get("required_tool")
    target_text = state["cleaned_data"]

    if tool_to_run == "query_service_metrics":
        # Extraer entidad objetivo (ej. pagos o inventario)
        service_target = "pagos" if "pago" in target_text.lower() else "inventario"
        metrics = query_service_metrics(service_target)

        return {
            "tool_payload": metrics,
            "required_tool": None,  # Limpiar la bandera tras la ejecución
            "audit_log": [
                f"PASO 4.1 (Tool Node): Ejecutada 'query_service_metrics' para '{service_target}' -> Estado: {metrics['status']}, Latencia: {metrics['latency_ms']}ms."
            ]
        }

    return {
        "audit_log": ["PASO 4.1 (Tool Node): No se especificó ninguna herramienta válida."]
    }