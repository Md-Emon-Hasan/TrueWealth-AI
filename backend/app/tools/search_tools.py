from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool


def get_duckduckgo_search():
    return DuckDuckGoSearchRun()


def get_yahoo_finance_news():
    return YahooFinanceNewsTool()
