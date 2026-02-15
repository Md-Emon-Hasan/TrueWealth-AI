from app.core.state import AgentState
from app.tools.vector_store import get_retriever

def retrieve_docs(state: AgentState):
    """RAG document retrieval"""
    retriever = get_retriever()
    ctx = "\n".join(state['conversation_history'])
    query = f"Context: {ctx}\nQuestion: {state['question']}" if ctx else state['question']
    
    docs = retriever.invoke(query)
    
    state['documents'] = docs
    state['rag_attempted'] = True
    state['search_query'] = query
    state['conversation_history'] += ["AI: Searching financial documents..."]
    state['source'] = 'rag_documents'
    
    return state