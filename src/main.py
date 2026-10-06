import sys
from pathlib import Path

# Garantiza que la raíz del proyecto esté en el path de importación
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.state import AgentState
from src.workflow.graph import create_agent_graph

def main():
    print("\n=======================================================")
    print("   SISTEMA MULTI-AGENTE CON HUMAN-IN-THE-LOOP (HITL)  ")
    print("=======================================================")

    app = create_agent_graph()

    # Cada ejecución con memoria requiere un thread_id único
    config = {"configurable": {"thread_id": "ticket-incidente-101"}}

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

    print("\n>>> INICIANDO EJECUCIÓN AUTÓNOMA INICIAL HASTA PUNTO DE PAUSA...")
    # Ejecutar hasta el punto de pausa configurado
    for event in app.stream(initial_state, config):
        for node_name, state_update in event.items():
            print(f"  [EJECUTADO NODO]: {node_name}")

    # Consultar el estado actual congelado en memoria
    snapshot = app.get_state(config)
    current_data = snapshot.values

    print("\n=======================================================")
    print(" ⏸️ SISTEMA PAUSADO POR REGLA DE SEGURIDAD (HITL)")
    print("=======================================================")
    if current_data.get("incident_report"):
        report = current_data["incident_report"]
        print(f"• Servicio afectado : {report['service_name']}")
        print(f"• Severidad estimada: {report['calculated_severity']}")
        print(f"• Impacto estimado  : {report['business_impact']}")
        print(f"• Acción sugerida   : {report['recommended_action']}")

    # Interacción humana simulada en consola
    decision = input("\n¿Autorizas el despacho de la alerta a los canales técnicos? (s/n): ").strip().lower()
    approved = decision == "s"

    print(f"\n>>> DECISIÓN DEL OPERADOR REGISTRADA: {'APROBADO' if approved else 'RECHAZADO'}")

    # Actualizar el estado en el checkpointer con la decisión del humano
    app.update_state(
        config,
        {
            "human_approved": approved,
            "human_feedback": "Aprobado por el Lead Engineer en turno" if approved else "Rechazado por falsa alarma",
            "audit_log": [f"HITL: Decisión humana registrada -> {'APROBADO' if approved else 'RECHAZADO'}."]
        }
    )

    print("\n>>> REANUDANDO FLUJO DESDE EL CHECKPOINT...")
    # Reanudar la ejecución pasando None para continuar donde se congeló
    for event in app.stream(None, config):
        for node_name, state_update in event.items():
            print(f"  [EJECUTADO NODO]: {node_name}")

    # Obtener el estado consolidado final
    final_snapshot = app.get_state(config)
    final_state = final_snapshot.values

    print("\n[TRAZA DE AUDITORÍA COMPLETA]:")
    for log in final_state["audit_log"]:
        print(f"  -> {log}")

    if final_state.get("notification_payload"):
        notif = final_state["notification_payload"]
        print("\n[DESPACHO EFECTIVO DE LA NOTIFICACIÓN]:")
        print(f"  Canal  : {notif['target_channel']}")
        print(f"  Asunto : {notif['subject']}")
        print(f"\n{notif['message_body']}")
    else:
        print("\n[DESPACHO OMITIDO]: La alerta fue descartada por decisión humana.")

    print("=======================================================\n")

if __name__ == "__main__":
    main()