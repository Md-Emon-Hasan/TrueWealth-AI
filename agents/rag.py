# agents/rag.py
from tools.vector_store import get_retriever
from core.state import AgentState

class RagAgent:
    @staticmethod
    def process(state: AgentState) -> AgentState:
        ctx = "\n".join(state['conversation_history'])
        query = f"Context: {ctx}\nQuestion: {state['question']}" if ctx else state['question']
        docs = get_retriever().invoke(query)
        state.update({
            "documents": docs,
            "rag_attempted": True,
            "search_query": query,
            "conversation_history": state['conversation_history'] + ["AI: Searching documents..."],
            "source": 'rag_documents'
        })
        return state