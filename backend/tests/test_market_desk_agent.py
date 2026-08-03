import asyncio
from unittest.mock import MagicMock, patch

from app.agents.market_desk_agent import market_desk_agent
from app.core.state import initialize_state


def _run(state):
    return asyncio.run(market_desk_agent(state))


def test_market_desk_combines_both_sources():
    state = initialize_state()
    state["question"] = "AAPL news"
    with patch('app.agents.market_desk_agent.get_yahoo_finance_news') as mock_yf, \
         patch('app.agents.market_desk_agent.get_duckduckgo_search') as mock_ddg:
        mock_yf.return_value = MagicMock(invoke=MagicMock(return_value="Apple news content"))
        mock_ddg.return_value = MagicMock(invoke=MagicMock(return_value="Apple web content"))
        result = _run(state)

    assert result["source"] == "market_desk"
    assert len(result["documents"]) == 2
    assert result["degraded"] == ""
    assert result["yfinance_attempted"] is True
    assert result["ddg_attempted"] is True


def test_market_desk_degrades_when_one_source_fails():
    state = initialize_state()
    state["question"] = "AAPL news"
    with patch('app.agents.market_desk_agent.get_yahoo_finance_news') as mock_yf, \
         patch('app.agents.market_desk_agent.get_duckduckgo_search') as mock_ddg:
        mock_yf.return_value = MagicMock(invoke=MagicMock(side_effect=Exception("timeout")))
        mock_ddg.return_value = MagicMock(invoke=MagicMock(return_value="Apple web content"))
        result = _run(state)

    assert len(result["documents"]) == 1
    assert result["degraded"] == "yfinance_unavailable"


def test_market_desk_degrades_when_both_sources_fail():
    state = initialize_state()
    state["question"] = "AAPL news"
    with patch('app.agents.market_desk_agent.get_yahoo_finance_news') as mock_yf, \
         patch('app.agents.market_desk_agent.get_duckduckgo_search') as mock_ddg:
        mock_yf.return_value = MagicMock(invoke=MagicMock(side_effect=Exception("timeout")))
        mock_ddg.return_value = MagicMock(invoke=MagicMock(side_effect=Exception("timeout")))
        result = _run(state)

    assert result["documents"] == []
    assert result["degraded"] == "market_desk_no_data"


def test_market_desk_extracts_ticker_from_full_sentence():
    state = initialize_state()
    state["question"] = "Any recent news on TSLA?"
    with patch('app.agents.market_desk_agent.get_yahoo_finance_news') as mock_yf, \
         patch('app.agents.market_desk_agent.get_duckduckgo_search') as mock_ddg:
        mock_yf.return_value = MagicMock(invoke=MagicMock(return_value="Tesla news content"))
        mock_ddg.return_value = MagicMock(invoke=MagicMock(return_value="Tesla web content"))
        _run(state)
        mock_yf.return_value.invoke.assert_called_once_with("TSLA")
        mock_ddg.return_value.invoke.assert_called_once_with("Any recent news on TSLA?")


def test_market_desk_treats_ticker_not_found_as_no_data():
    state = initialize_state()
    state["question"] = "Any recent news on TSLA?"
    with patch('app.agents.market_desk_agent.get_yahoo_finance_news') as mock_yf, \
         patch('app.agents.market_desk_agent.get_duckduckgo_search') as mock_ddg:
        mock_yf.return_value = MagicMock(invoke=MagicMock(return_value="Company ticker TSLA not found."))
        mock_ddg.return_value = MagicMock(invoke=MagicMock(return_value="Tesla web content"))
        result = _run(state)
        assert len(result["documents"]) == 1
        assert result["documents"][0].page_content == "Tesla web content"


def test_market_desk_uses_cache_on_second_call():
    state = initialize_state()
    state["question"] = "AAPL news"
    with patch('app.agents.market_desk_agent.get_yahoo_finance_news') as mock_yf, \
         patch('app.agents.market_desk_agent.get_duckduckgo_search') as mock_ddg:
        mock_yf.return_value = MagicMock(invoke=MagicMock(return_value="Apple news content"))
        mock_ddg.return_value = MagicMock(invoke=MagicMock(return_value="Apple web content"))
        _run(dict(state))
        _run(dict(state))
        assert mock_yf.return_value.invoke.call_count == 1
        assert mock_ddg.return_value.invoke.call_count == 1
