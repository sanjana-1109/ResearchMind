from typing import TypedDict

class AgentState(TypedDict):
    query: str
    session_id: str
    mode: str
    vector_db: object
    bm25: object
    context: str
    answer: str
    sources: list
    is_report: bool
    plan: list