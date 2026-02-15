from langchain_core.documents import Document
from app.core.state import AgentState
from app.tools.search_tools import get_duckduckgo_search

def retrieve_duckduckgo(state: AgentState):
    """DuckDuckGo Search Fallback"""
    duckduckgo_search = get_duckduckgo_search()
    content = duckduckgo_search.invoke(state['question'])
    
    state['documents'] = [Document(page_content=content)]
    state['ddg_attempted'] = True
    state['source'] = 'duckduckgo'
    state['conversation_history'] += ["AI: Searching DuckDuckGo..."]
    
    return state