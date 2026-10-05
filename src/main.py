import os
import operator
from typing import Annotated, Literal, TypedDict, List
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# ---------------------------------------------------------------------------
# 0. CONFIGURACIÓN Y CLIENTE LLM (CONSUMO EXTERNO)
# ---------------------------------------------------------------------------
# Carga las credenciales del archivo .env local
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Inicialización del adaptador de Google GenAI
# NOTA: Si GEMINI_API_KEY no está definida, se mantiene en None y se capturará
# una excepción controlada durante la ejecución del nodo para evitar caídas críticas.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0.3
) if api_key else None


# ---------------------------------------------------------------------------
# 1. DEFINICIÓN DEL ESTADO (DTO INMUTABLE COMPARTIDO)
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    input_message: str
    cleaned_data: str
    ai_analysis: str  # Campo donde almacenamos la respuesta del LLM
    audit_log: Annotated[List[str], operator.add]  # Lista acumulativa
    retry_count: int
    is_valid: bool


# ---------------------------------------------------------------------------
# 2. NODOS DE PROCESAMIENTO
# ---------------------------------------------------------------------------
def input_cleaner_node(state: AgentState) -> dict:
    """Nodo 1: Sanea espacios de la entrada y genera traza de auditoría."""
    raw_text = state["input_message"].strip()
    return {
        "cleaned_data": raw_text,
        "audit_log": [f"PASO 1 (Cleaner): Entrada normalizada -> '{raw_text}'"]
    }


def validator_node(state: AgentState) -> dict:
    """
    Nodo 2: Valida reglas de negocio sobre los datos saneados.
    Regla: El mensaje debe tener al menos 10 caracteres.
    """
    current_text = state["cleaned_data"]
    attempts = state.get("retry_count", 0) + 1
    valid = len(current_text) >= 10

    return {
        "is_valid": valid,
        "retry_count": attempts,
        "audit_log": [f"PASO 2 (Validator - Intento {attempts}): Regla de longitud {'CUMPLIDA' if valid else 'INCUMPLIDA'}."]
    }


def auto_fixer_node(state: AgentState) -> dict:
    """Nodo 3: Aplica corrección automática para superar la validación."""
    fixed_text = state["cleaned_data"] + " [SOLICITUD_COMPLETA]"
    return {
        "cleaned_data": fixed_text,
        "audit_log": [f"PASO 3 (Auto-Fixer): Texto corregido -> '{fixed_text}'"]
    }


def gemini_enricher_node(state: AgentState) -> dict:
    """
    Nodo 4: Consumo real del modelo Gemini.
    Toma los datos validados, consulta a la API de Google GenAI y actualiza el estado.
    """
    text_to_analyze = state["cleaned_data"]

    # Verificación de precondición: API Key disponible
    if not llm:
        fallback_msg = "[MODO OFFLINE]: No se detectó GEMINI_API_KEY en .env. Consumo simulado."
        return {
            "ai_analysis": fallback_msg,
            "audit_log": [f"PASO 4 (Gemini Node): {fallback_msg}"]
        }

    try:
        # CONEXIÓN Y LLAMADA A LA API DE GEMINI:
        messages = [
            SystemMessage(content="Eres un analista de software backend. Clasifica la intención del usuario y resume en una frase concisa."),
            HumanMessage(content=text_to_analyze)
        ]
        
        # Invocación sincrónica al modelo LLM
        response = llm.invoke(messages)
        ai_result = response.content.strip()

        return {
            "ai_analysis": ai_result,
            "audit_log": [f"PASO 4 (Gemini Node): Respuesta recibida de Gemini 2.5 Flash exitosamente."]
        }

    except Exception as ex:
        error_msg = f"[ERROR CONSUMO GEMINI]: {str(ex)}"
        return {
            "ai_analysis": error_msg,
            "audit_log": [f"PASO 4 (Gemini Node Fallo): {error_msg}"]
        }


def final_processor_node(state: AgentState) -> dict:
    """Nodo 5: Consolidador final del pipeline."""
    return {
        "audit_log": ["PASO 5 (Final Processor): Pipeline finalizado. Estado consolidado."]
    }


# ---------------------------------------------------------------------------
# 3. ROUTER / ARISTAS CONDICIONALES
# ---------------------------------------------------------------------------
def check_validation_route(state: AgentState) -> Literal["gemini_enricher", "auto_fixer", "fail_exit"]:
    """
    Evalúa la validez de los datos:
    - Válido -> Pasa al consumo del LLM (Gemini).
    - Inválido y reintentos < 2 -> Bucle de auto-corrección.
    - Inválido persistente -> Salida sin ejecutar consumo.
    """
    if state["is_valid"]:
        return "gemini_enricher"
    
    if state["retry_count"] < 2:
        return "auto_fixer"
        
    return "fail_exit"


# ---------------------------------------------------------------------------
# 4. ENSAMBLADO DEL GRAFO (WORKFLOW)
# ---------------------------------------------------------------------------
workflow = StateGraph(AgentState)

# Registro de Nodos
workflow.add_node("input_cleaner", input_cleaner_node)
workflow.add_node("validator", validator_node)
workflow.add_node("auto_fixer", auto_fixer_node)
workflow.add_node("gemini_enricher", gemini_enricher_node)
workflow.add_node("final_processor", final_processor_node)

# Flujo secuencial inicial
workflow.add_edge(START, "input_cleaner")
workflow.add_edge("input_cleaner", "validator")

# Arista Condicional (Self-Correction Loop o Salto a IA)
workflow.add_conditional_edges(
    "validator",
    check_validation_route,
    {
        "gemini_enricher": "gemini_enricher",
        "auto_fixer": "auto_fixer",
        "fail_exit": END
    }
)

# Retorno del auto-corrector al validador para re-chequeo
workflow.add_edge("auto_fixer", "validator")

# Secuencia posterior a la llamada IA
workflow.add_edge("gemini_enricher", "final_processor")
workflow.add_edge("final_processor", END)

# Compilación
app = workflow.compile()


# ---------------------------------------------------------------------------
# 5. EJECUCIÓN Y PRUEBAS
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n=======================================================")
    print("      EJECUCIÓN DEL PIPELINE CON INTEGRACIÓN GEMINI     ")
    print("=======================================================")

    test_state: AgentState = {
        "input_message": "  Fallo al conectar la base de datos PostgreSQL  ",
        "cleaned_data": "",
        "ai_analysis": "",
        "audit_log": [],
        "retry_count": 0,
        "is_valid": False
    }

    final_result = app.invoke(test_state)

    print("\n[TRAZA DE AUDITORÍA]:")
    for log in final_result["audit_log"]:
        print(f"  -> {log}")

    print("\n[RESPUESTA MODELO IA]:")
    print(f"  {final_result['ai_analysis']}")
    print("=======================================================\n")