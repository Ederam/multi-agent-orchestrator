from src.core.state import AgentState
from src.workflow.graph import create_agent_graph

def main():
    print("\n=======================================================")
    print("   EJECUCIÓN DEL SISTEMA MULTI-AGENTE (MODULAR)       ")
    print("=======================================================")

    # Instanciar el grafo compilado
    app = create_agent_graph()

    # Estado de prueba
    test_state: AgentState = {
        "input_message": "  Error de timeout al consultar microservicio de pagos  ",
        "cleaned_data": "",
        "ai_analysis": "",
        "audit_log": [],
        "retry_count": 0,
        "is_valid": False
    }

    # Ejecutar el flujo
    final_result = app.invoke(test_state)

    print("\n[TRAZA DE AUDITORÍA]:")
    for log in final_result["audit_log"]:
        print(f"  -> {log}")

    print("\n[RESPUESTA MODELO IA]:")
    print(f"  {final_result['ai_analysis']}")
    print("=======================================================\n")

if __name__ == "__main__":
    main()