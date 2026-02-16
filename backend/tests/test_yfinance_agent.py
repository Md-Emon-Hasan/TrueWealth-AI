from unittest.mock import MagicMock, patch

from app.agents.yfinance import retrieve_yfinance
from app.core.state import initialize_state


def test_retrieve_yfinance():
    state = initialize_state()
    state["question"] = "AAPL"
    with patch('app.agents.yfinance.get_yahoo_finance_news') as mock_search:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = "YFinance Result"
        mock_search.return_value = mock_instance
        result = retrieve_yfinance(state)
        assert result["yfinance_attempted"] is True
        assert result["source"] == "yfinance"
        assert "YFinance Result" in result["documents"][0].page_content
