import operator
from typing import Annotated, List, TypedDict

class AgentState(TypedDict):
    input_message: str
    cleaned_data: str
    ai_analysis: str
    required_tool: str | None
    tool_payload: dict | None
    incident_report: dict | None
    notification_payload: dict | None  # Datos listos para despacho (asunto, canal, mensaje)
    audit_log: Annotated[List[str], operator.add]
    retry_count: int
    is_valid: bool