from typing import TypedDict, List, Optional
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