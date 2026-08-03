from app.agents.compliance_officer_agent import ComplianceOfficerAgent
from app.core.cache import RAG_INDEX_VERSION, cache_get, cache_set, rag_cache
from app.core.state import AgentState
from app.tools.vector_store import get_retriever

_compliance = ComplianceOfficerAgent()


def retrieve_docs(state: AgentState):
    """RAG document retrieval"""
    ctx = "\n".join(state['conversation_history'])
    query = f"Context: {ctx}\nQuestion: {state['question']}" if ctx else state['question']

    cache_key = (RAG_INDEX_VERSION, query)
    docs = cache_get(rag_cache, cache_key)
    if docs is None:
        retriever = get_retriever()
        docs = retriever.invoke(query)
        for doc in docs:
            doc.page_content = _compliance.sanitize_input(doc.page_content)
        cache_set(rag_cache, cache_key, docs)

    state['documents'] = docs
    state['rag_attempted'] = True
    state['search_query'] = query
    state['conversation_history'] += ["AI: Searching financial documents..."]
    state['source'] = 'rag_documents'

    return state
