from app.core.cache import RAG_INDEX_VERSION, cache_get, cache_set, rag_cache
from app.core.state import AgentState
from app.tools.vector_store import get_retriever


def retrieve_docs(state: AgentState):
    """RAG document retrieval"""
    ctx = "\n".join(state['conversation_history'])
    query = f"Context: {ctx}\nQuestion: {state['question']}" if ctx else state['question']

    cache_key = (RAG_INDEX_VERSION, query)
    docs = cache_get(rag_cache, cache_key)
    if docs is None:
        retriever = get_retriever()
        docs = retriever.invoke(query)
        cache_set(rag_cache, cache_key, docs)

    state['documents'] = docs
    state['rag_attempted'] = True
    state['search_query'] = query
    state['conversation_history'] += ["AI: Searching financial documents..."]
    state['source'] = 'rag_documents'

    return state
