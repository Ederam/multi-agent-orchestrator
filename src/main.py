import sys
from pathlib import Path

# Garantiza que la raíz del proyecto esté en el path de importación
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.state import AgentState
from src.workflow.graph import create_agent_graph

def main():
    print("\n=======================================================")
    print("   SISTEMA MULTI-AGENTE AUTÓNOMO: PIPELINE COMPLETO   ")
    print("=======================================================")

    app = create_agent_graph()

    test_state: AgentState = {
        "input_message": "  Error de timeout al consultar microservicio de pagos  ",
        "cleaned_data": "",
        "ai_analysis": "",
        "required_tool": None,
        "tool_payload": None,
        "incident_report": None,
        "notification_payload": None,
        "audit_log": [],
        "retry_count": 0,
        "is_valid": False
    }

    final_result = app.invoke(test_state)

    print("\n[TRAZA DE AUDITORÍA]:")
    for log in final_result["audit_log"]:
        print(f"  -> {log}")

    print("\n[1. DECISIÓN DEL AGENTE ROUTER]:")
    print(f"  {final_result['ai_analysis']}")

    if final_result.get("incident_report"):
        print("\n[2. ANÁLISIS DEL AGENTE SINTETIZADOR]:")
        for key, value in final_result["incident_report"].items():
            print(f"  * {key.upper()}: {value}")

    if final_result.get("notification_payload"):
        notif = final_result["notification_payload"]
        print("\n[3. DESPACHO DEL AGENTE NOTIFICADOR]:")
        print(f"  Canal Destino : {notif['target_channel']}")
        print(f"  Asunto        : {notif['subject']}")
        print(f"\n{notif['message_body']}")

    print("=======================================================\n")

if __name__ == "__main__":
    main()