import sys
from pathlib import Path

# Garantiza que la raíz del proyecto esté en el path de importación
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.state import AgentState
from src.workflow.graph import create_agent_graph
from src.services.telemetry import ExecutionTracer

def main():
    print("\n=======================================================")
    print("   SISTEMA MULTI-AGENTE: OBSERVABILIDAD Y AUDITORÍA   ")
    print("=======================================================")

    tracer = ExecutionTracer()
    app = create_agent_graph()

    config = {"configurable": {"thread_id": "incident-trace-2026"}}

    initial_state: AgentState = {
        "input_message": "  Error de timeout al consultar microservicio de pagos  ",
        "cleaned_data": "",
        "ai_analysis": "",
        "required_tool": None,
        "tool_payload": None,
        "incident_report": None,
        "notification_payload": None,
        "human_approved": None,
        "human_feedback": None,
        "audit_log": [],
        "retry_count": 0,
        "is_valid": False
    }

    print("\n>>> EJECUTANDO PIPELINE HASTA PUNTO DE INTERRUPCIÓN (HITL)...")
    for event in app.stream(initial_state, config):
        for node_name in event.keys():
            tracer.mark_node(node_name)
            print(f"  [NODO FINALIZADO]: {node_name}")

    # Consultar estado en pausa
    snapshot = app.get_state(config)
    current_data = snapshot.values

    print("\n=======================================================")
    print(" ⏸️ SISTEMA EN PAUSA: REVISIÓN DE INCIDENTE")
    print("=======================================================")
    if current_data.get("incident_report"):
        report = current_data["incident_report"]
        print(f"• Servicio  : {report['service_name']}")
        print(f"• Severidad : {report['calculated_severity']}")
        print(f"• Impacto   : {report['business_impact']}")
        print(f"• Acción    : {report['recommended_action']}")

    # Decisión humana en consola
    decision = input("\n¿Aprobar el despacho de la notificación? (s/n): ").strip().lower()
    approved = decision == "s"

    app.update_state(
        config,
        {
            "human_approved": approved,
            "human_feedback": "Aprobación técnica de guardia" if approved else "Descartado por mantenimiento programado",
            "audit_log": [f"HITL: Decisión manual -> {'APROBADO' if approved else 'RECHAZADO'}."]
        }
    )

    print("\n>>> REANUDANDO PIPELINE TRAS DECISIÓN...")
    for event in app.stream(None, config):
        for node_name in event.keys():
            tracer.mark_node(node_name)
            print(f"  [NODO FINALIZADO]: {node_name}")

    final_state = app.get_state(config).values

    # Exportar auditoría a JSON
    log_file = tracer.export_audit_log(final_state)

    print("\n=======================================================")
    print("        RESULTADO DEL PIPELINE Y OBSERVABILIDAD       ")
    print("=======================================================")
    print(f"✔️ Archivo de Auditoría Exportado: {log_file}")
    
    if final_state.get("notification_payload"):
        print(f"✔️ Notificación despachada al canal: {final_state['notification_payload']['target_channel']}")
    else:
        print("✔️ Despacho cancelado conforme a decisión humana.")
        
    print("=======================================================\n")

if __name__ == "__main__":
    main()