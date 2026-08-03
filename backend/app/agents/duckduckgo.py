from app.core.cache import cache_get, cache_set, ddg_cache
from app.core.resilience import call_with_timeout
from app.core.state import AgentState
from app.tools.search_tools import get_duckduckgo_search
from langchain_core.documents import Document


def retrieve_duckduckgo(state: AgentState):
    """DuckDuckGo Search Fallback"""
    query = state['question']
    degraded = ""

    content = cache_get(ddg_cache, query)
    if content is None:
        duckduckgo_search = get_duckduckgo_search()
        try:
            content = call_with_timeout(duckduckgo_search.invoke, query)
        except Exception:
            content = ""
            degraded = "duckduckgo_unavailable"

        if content and content.strip():
            cache_set(ddg_cache, query, content)
        else:
            content = ""
            degraded = degraded or "duckduckgo_no_data"

    state['documents'] = [Document(page_content=content)] if content else []
    state['ddg_attempted'] = True
    state['source'] = 'duckduckgo'
    state['degraded'] = degraded
    state['conversation_history'] += ["AI: Searching DuckDuckGo..."]

    return state
