import operator
from typing import Annotated, List, TypedDict

class AgentState(TypedDict):
    input_message: str
    cleaned_data: str
    ai_analysis: str
    audit_log: Annotated[List[str], operator.add]  # Reducer acumulativo
    retry_count: int
    is_valid: bool