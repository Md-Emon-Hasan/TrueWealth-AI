from app.core.cache import cache_get, cache_set, news_cache
from app.core.resilience import call_with_timeout
from app.core.state import AgentState
from app.tools.search_tools import get_yahoo_finance_news
from langchain_core.documents import Document


def retrieve_yfinance(state: AgentState):
    """Yahoo Finance News Tool fallback"""
    query = state['question']
    degraded = ""

    content = cache_get(news_cache, query)
    if content is None:
        yahoo_finance_news = get_yahoo_finance_news()
        try:
            content = call_with_timeout(yahoo_finance_news.invoke, query)
        except Exception:
            content = ""
            degraded = "yfinance_unavailable"

        if content and content.strip():
            cache_set(news_cache, query, content)
        else:
            content = ""
            degraded = degraded or "yfinance_no_data"

    state['documents'] = [Document(page_content=content)] if content else []
    state['yfinance_attempted'] = True
    state['source'] = 'yfinance'
    state['degraded'] = degraded
    state['conversation_history'] += ["AI: Searching yfinance..."]

    return state
