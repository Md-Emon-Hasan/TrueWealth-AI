# core/state.py
from typing import TypedDict
from typing import List
from typing import Optional
from langchain.schema import Document

class AgentState(TypedDict):
    question: str
    documents: List[Document]
    generation: str
    source: str
    search_query: Optional[str]
    conversation_history: List[str]
    llm_attempted: bool
    rag_attempted: bool
    yfinance_attempted: bool
    ddg_attempted: bool
    retry_count: int
    memory: List[str]

def initialize_state() -> AgentState:
    return {
        "question": "",
        "documents": [],
        "generation": "",
        "source": "",
        "search_query": None,
        "conversation_history": [],
        "llm_attempted": False,
        "rag_attempted": False,
        "yfinance_attempted": False,
        "ddg_attempted": False,
        "retry_count": 0,
        "memory": []
    }