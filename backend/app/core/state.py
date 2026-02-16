from typing import List, TypedDict


class AgentState(TypedDict):
    question: str
    generation: str
    documents: List[object]
    source: str
    retry_count: int
    memory: List[str]
    conversation_history: List[str]
    llm_attempted: bool
    rag_attempted: bool
    yfinance_attempted: bool
    ddg_attempted: bool
    retry_count: int
    search_query: str


def initialize_state() -> AgentState:
    return {
        "question": "",
        "generation": "",
        "documents": [],
        "source": "",
        "retry_count": 0,
        "memory": [],
        "conversation_history": [],
        "llm_attempted": False,
        "rag_attempted": False,
        "yfinance_attempted": False,
        "ddg_attempted": False,
        "search_query": ""
    }
