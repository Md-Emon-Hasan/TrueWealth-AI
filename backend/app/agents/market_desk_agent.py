import asyncio
import re

from app.agents.compliance_officer_agent import ComplianceOfficerAgent
from app.core.cache import cache_get, cache_set, ddg_cache, news_cache
from app.core.config import MARKET_DESK_TIMEOUT_SECONDS
from app.core.state import AgentState
from app.tools.search_tools import get_duckduckgo_search, get_yahoo_finance_news
from langchain_core.documents import Document

_compliance = ComplianceOfficerAgent()
_TICKER_PATTERN = re.compile(r"\b[A-Z]{2,5}\b")


def _extract_ticker(question):
    match = _TICKER_PATTERN.search(question)
    return match.group(0) if match else question


async def _fetch_yfinance_news(question):
    query = _extract_ticker(question)
    cached = cache_get(news_cache, query)
    if cached is not None:
        return cached, ""
    try:
        content = await asyncio.wait_for(
            asyncio.to_thread(get_yahoo_finance_news().invoke, query), timeout=MARKET_DESK_TIMEOUT_SECONDS
        )
    except Exception:
        return "", "yfinance_unavailable"
    if not content or not content.strip() or content.startswith("Company ticker") or content.startswith("No news"):
        return "", "yfinance_no_data"
    content = _compliance.sanitize_input(content)
    cache_set(news_cache, query, content)
    return content, ""


async def _fetch_duckduckgo(query):
    cached = cache_get(ddg_cache, query)
    if cached is not None:
        return cached, ""
    try:
        content = await asyncio.wait_for(
            asyncio.to_thread(get_duckduckgo_search().invoke, query), timeout=MARKET_DESK_TIMEOUT_SECONDS
        )
    except Exception:
        return "", "duckduckgo_unavailable"
    if not content or not content.strip():
        return "", "duckduckgo_no_data"
    content = _compliance.sanitize_input(content)
    cache_set(ddg_cache, query, content)
    return content, ""


async def market_desk_agent(state: AgentState):
    """Coordinates yfinance news and DuckDuckGo web search in parallel for market-intelligence queries"""
    query = state['question']

    (yf_content, yf_degraded), (ddg_content, ddg_degraded) = await asyncio.gather(
        _fetch_yfinance_news(query), _fetch_duckduckgo(query)
    )

    documents = [Document(page_content=c) for c in (yf_content, ddg_content) if c]
    degraded_parts = [d for d in (yf_degraded, ddg_degraded) if d]

    state['documents'] = documents
    state['yfinance_attempted'] = True
    state['ddg_attempted'] = True
    state['source'] = 'market_desk'
    state['degraded'] = "market_desk_no_data" if not documents else ",".join(degraded_parts)
    state['conversation_history'] += ["AI: Checking live market data and news..."]

    return state
