"""
Módulo de Telemetría y Observabilidad.
Permite estructurar, calcular métricas de ejecución y exportar la auditoría a JSON.
"""

import json
import time
from datetime import datetime
from pathlib import Path

class ExecutionTracer:
    """Rastreador de tiempo y métricas del pipeline agéntico."""
    def __init__(self):
        self.start_time = time.time()
        self.node_timestamps = {}

    def mark_node(self, node_name: str):
        """Registra el timestamp de finalización de un nodo."""
        self.node_timestamps[node_name] = round(time.time() - self.start_time, 4)

    def export_audit_log(self, state: dict, output_dir: str = "logs") -> str:
        """Exporta el estado final consolidado y las métricas a un archivo JSON estructurado."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/audit_trace_{timestamp_str}.json"

        audit_payload = {
            "metadata": {
                "trace_id": f"trace-{timestamp_str}",
                "total_duration_seconds": round(time.time() - self.start_time, 4),
                "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                "human_in_the_loop": {
                    "approved": state.get("human_approved"),
                    "feedback": state.get("human_feedback")
                }
            },
            "metrics": {
                "retry_count": state.get("retry_count", 0),
                "nodes_duration_timeline": self.node_timestamps
            },
            "pipeline_state": {
                "input_message": state.get("input_message"),
                "cleaned_data": state.get("cleaned_data"),
                "ai_decision": state.get("ai_analysis"),
                "tool_payload": state.get("tool_payload"),
                "incident_report": state.get("incident_report"),
                "notification_payload": state.get("notification_payload")
            },
            "audit_trail": state.get("audit_log", [])
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(audit_payload, f, indent=2, ensure_ascii=False)

        return filename