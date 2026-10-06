"""
Módulo de Herramientas (Tools / Servicing Layer).
Define funciones ejecutables especializadas que el agente puede invocar de forma autónoma.
"""

def query_service_metrics(service_name: str) -> dict:
    """
    Herramienta de diagnóstico de infraestructura.
    Consulta el estado de salud, latencia y disponibilidad de un microservicio.
    """
    service_clean = service_name.lower().strip()
    
    # Base de datos simulada de telemetría de servicios
    metrics_catalog = {
        "pagos": {
            "service": "payments-gateway-api",
            "status": "DEGRADED",
            "latency_ms": 4850,
            "error_rate_pct": 28.4,
            "active_circuit_breaker": True,
            "last_incident": "Timeout recurrente hacia adquirente externo"
        },
        "inventario": {
            "service": "inventory-mgmt-service",
            "status": "HEALTHY",
            "latency_ms": 85,
            "error_rate_pct": 0.1,
            "active_circuit_breaker": False,
            "last_incident": "Ninguno en las últimas 24h"
        }
    }

    # Búsqueda por coincidencia
    for key, data in metrics_catalog.items():
        if key in service_clean:
            return data

    return {
        "service": service_name,
        "status": "UNKNOWN",
        "latency_ms": 0,
        "error_rate_pct": 0.0,
        "active_circuit_breaker": False,
        "message": f"No se encontraron métricas históricas para '{service_name}'"
    }