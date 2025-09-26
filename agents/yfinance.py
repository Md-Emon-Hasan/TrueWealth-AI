from langchain.schema import Document
from core.state import AgentState
from tools.search_tools import get_yahoo_finance_news

def retrieve_yfinance(state: AgentState):
    """Yahoo Finance News Tool fallback"""
    yahoo_finance_news = get_yahoo_finance_news()
    content = yahoo_finance_news.invoke(state['question'])
    
    state['documents'] = [Document(page_content=content)]
    state['yfinance_attempted'] = True
    state['source'] = 'yfinance'
    state['conversation_history'] += ["AI: Searching yfinance..."]
    
    return state