import operator
from typing import Annotated, List, TypedDict

class AgentState(TypedDict):
    input_message: str
    cleaned_data: str
    ai_analysis: str
    required_tool: str | None     # Nombre de la herramienta que el agente solicita ejecutar
    tool_payload: dict | None      # Datos recuperados tras ejecutar la herramienta
    audit_log: Annotated[List[str], operator.add]
    retry_count: int
    is_valid: bool