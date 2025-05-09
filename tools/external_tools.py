from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool

def load_tools():
    return {
        "duckduckgo": DuckDuckGoSearchRun(),
        "yfinance": YahooFinanceNewsTool(),
    }