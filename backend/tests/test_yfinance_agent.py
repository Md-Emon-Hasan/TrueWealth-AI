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
        assert result["degraded"] == ""


def test_retrieve_yfinance_empty_result_is_degraded():
    state = initialize_state()
    state["question"] = "UNKNOWNTICKER"
    with patch('app.agents.yfinance.get_yahoo_finance_news') as mock_search:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = ""
        mock_search.return_value = mock_instance
        result = retrieve_yfinance(state)
        assert result["documents"] == []
        assert result["degraded"] == "yfinance_no_data"


def test_retrieve_yfinance_error_is_degraded():
    state = initialize_state()
    state["question"] = "AAPL"
    with patch('app.agents.yfinance.get_yahoo_finance_news') as mock_search:
        mock_instance = MagicMock()
        mock_instance.invoke.side_effect = Exception("timeout")
        mock_search.return_value = mock_instance
        result = retrieve_yfinance(state)
        assert result["documents"] == []
        assert result["degraded"] == "yfinance_unavailable"


def test_retrieve_yfinance_uses_cache_on_second_call():
    state = initialize_state()
    state["question"] = "AAPL"
    with patch('app.agents.yfinance.get_yahoo_finance_news') as mock_search:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = "cached news"
        mock_search.return_value = mock_instance
        retrieve_yfinance(dict(state))
        retrieve_yfinance(dict(state))
        assert mock_instance.invoke.call_count == 1
