from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool

def get_duckduckgo_search():
    """Get DuckDuckGo search tool"""
    return DuckDuckGoSearchRun()

def get_yahoo_finance_news():
    """Get Yahoo Finance news tool"""
    return YahooFinanceNewsTool()