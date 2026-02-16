from unittest.mock import patch

from app.tools.llm_client import get_llm
from app.tools.search_tools import (get_duckduckgo_search,
                                    get_yahoo_finance_news)


def test_tools_getters():
    # Test tool getter functions to cover those lines
    with patch('app.tools.llm_client.ChatGroq') as mock_groq:
        get_llm()
        mock_groq.assert_called_once()

    with patch('app.tools.search_tools.DuckDuckGoSearchRun') as mock_ddg:
        get_duckduckgo_search()
        mock_ddg.assert_called_once()

    with patch('app.tools.search_tools.YahooFinanceNewsTool') as mock_yfn:
        get_yahoo_finance_news()
        mock_yfn.assert_called_once()
