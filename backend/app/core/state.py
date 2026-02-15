from typing import TypedDict, Annotated, List, Union, Optional
from langchain_core.documents import Document
import operator

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

def initialize_state():
    """Initialize conversation state"""
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