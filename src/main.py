import sys
from pathlib import Path

# Garantiza que la raíz del proyecto esté en el path de importación
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.core.state import AgentState
from src.workflow.graph import create_agent_graph

def main():
    print("\n=======================================================")
    print("   SISTEMA MULTI-AGENTE AUTÓNOMO CON TOOL CALLING     ")
    print("=======================================================")

    app = create_agent_graph()

    test_state: AgentState = {
        "input_message": "  Error de timeout al consultar microservicio de pagos  ",
        "cleaned_data": "",
        "ai_analysis": "",
        "required_tool": None,
        "tool_payload": None,
        "audit_log": [],
        "retry_count": 0,
        "is_valid": False
    }

    final_result = app.invoke(test_state)

    print("\n[TRAZA DE AUDITORÍA]:")
    for log in final_result["audit_log"]:
        print(f"  -> {log}")

    print("\n[DECISIÓN DEL AGENTE]:")
    print(f"  {final_result['ai_analysis']}")

    if final_result.get("tool_payload"):
        print("\n[DATOS RECUPERADOS POR LA HERRAMIENTA (TOOL PAYLOAD)]:")
        for key, value in final_result["tool_payload"].items():
            print(f"  * {key}: {value}")

    print("=======================================================\n")

if __name__ == "__main__":
    main()