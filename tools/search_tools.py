# tools/search_tools.py
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool

_ddg = None
_yfinance = None

def get_ddg_tool():
    global _ddg
    if _ddg is None:
        _ddg = DuckDuckGoSearchRun()
    return _ddg

def get_yfinance_tool():
    global _yfinance
    if _yfinance is None:
        _yfinance = YahooFinanceNewsTool()
    return _yfinance