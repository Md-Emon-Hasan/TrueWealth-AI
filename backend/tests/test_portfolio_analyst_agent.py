import asyncio
from unittest.mock import MagicMock, patch

import pandas as pd

from app.agents.portfolio_analyst_agent import portfolio_analyst_agent
from app.core.state import initialize_state


def _run(state):
    return asyncio.run(portfolio_analyst_agent(state))


def _history(prices):
    dates = pd.date_range("2026-01-01", periods=len(prices))
    return pd.DataFrame({"Close": prices}, index=dates)


def _mock_ticker_side_effect(histories):
    def _ticker(symbol):
        mock = MagicMock()
        mock.history.return_value = histories.get(symbol, pd.DataFrame())
        return mock
    return _ticker


def test_computes_real_metrics_from_structured_portfolio():
    state = initialize_state()
    state["question"] = "how is my portfolio doing"
    state["portfolio_input"] = [{"ticker": "AAPL", "shares": 10}, {"ticker": "MSFT", "shares": 5}]

    histories = {
        "AAPL": _history([100, 102, 101, 105, 110]),
        "MSFT": _history([200, 198, 202, 205, 210]),
    }
    with patch('app.agents.portfolio_analyst_agent.yf.Ticker', side_effect=_mock_ticker_side_effect(histories)):
        with patch('app.agents.portfolio_analyst_agent.get_llm') as mock_llm:
            mock_llm.return_value = MagicMock(invoke=MagicMock(
                return_value=MagicMock(content="Your portfolio is diversified.", model_used="m",
                                        fallback_used=False, degraded=None)
            ))
            result = _run(state)

    metrics = result["portfolio_analysis"]
    assert metrics["total_value"] == 10 * 110 + 5 * 210
    assert "AAPL" in metrics["allocation_pct"]
    assert result["source"] == "portfolio_analysis"
    assert result["generation"] == "Your portfolio is diversified."


def test_parses_holdings_from_free_text_when_no_structured_input():
    state = initialize_state()
    state["question"] = "I hold 10 shares of AAPL, what's my risk?"

    histories = {"AAPL": _history([100, 101, 99, 103, 105])}
    with patch('app.agents.portfolio_analyst_agent.yf.Ticker', side_effect=_mock_ticker_side_effect(histories)):
        with patch('app.agents.portfolio_analyst_agent.get_llm') as mock_llm:
            mock_llm.return_value = MagicMock(invoke=MagicMock(
                return_value=MagicMock(content="Single holding.", model_used="m", fallback_used=False, degraded=None)
            ))
            result = _run(state)

    assert result["portfolio_analysis"]["total_value"] == 10 * 105


def test_no_holdings_identified_degrades_gracefully():
    state = initialize_state()
    state["question"] = "how should I invest generally"

    result = _run(state)

    assert result["degraded"] == "portfolio_not_parsed"
    assert "couldn't identify your holdings" in result["generation"]


def test_missing_ticker_data_is_excluded_not_fatal():
    state = initialize_state()
    state["portfolio_input"] = [{"ticker": "AAPL", "shares": 10}, {"ticker": "FAKEZ", "shares": 5}]
    state["question"] = "my portfolio"

    histories = {"AAPL": _history([100, 101, 102, 103, 104])}
    with patch('app.agents.portfolio_analyst_agent.yf.Ticker', side_effect=_mock_ticker_side_effect(histories)):
        with patch('app.agents.portfolio_analyst_agent.get_llm') as mock_llm:
            mock_llm.return_value = MagicMock(invoke=MagicMock(
                return_value=MagicMock(content="Partial data.", model_used="m", fallback_used=False, degraded=None)
            ))
            result = _run(state)

    assert "FAKEZ" in result["degraded"]
    assert result["portfolio_analysis"]["total_value"] == 10 * 104


def test_all_tickers_unavailable_degrades_gracefully():
    state = initialize_state()
    state["portfolio_input"] = [{"ticker": "FAKEZ", "shares": 5}]
    state["question"] = "my portfolio"

    with patch('app.agents.portfolio_analyst_agent.yf.Ticker', side_effect=_mock_ticker_side_effect({})):
        result = _run(state)

    assert result["degraded"] == "portfolio_data_unavailable"
    assert result["documents"] == []


def test_ticker_fetch_exception_is_excluded_not_fatal():
    state = initialize_state()
    state["portfolio_input"] = [{"ticker": "AAPL", "shares": 10}, {"ticker": "BADTICK", "shares": 5}]
    state["question"] = "my portfolio"

    def ticker_side_effect(symbol):
        if symbol == "BADTICK":
            raise Exception("network error")
        mock = MagicMock()
        mock.history.return_value = _history([100, 101, 102, 103, 104])
        return mock

    with patch('app.agents.portfolio_analyst_agent.yf.Ticker', side_effect=ticker_side_effect):
        with patch('app.agents.portfolio_analyst_agent.get_llm') as mock_llm:
            mock_llm.return_value = MagicMock(invoke=MagicMock(
                return_value=MagicMock(content="Partial data.", model_used="m", fallback_used=False, degraded=None)
            ))
            result = _run(state)

    assert "BADTICK" in result["degraded"]
    assert result["portfolio_analysis"]["total_value"] == 10 * 104


def test_no_concentration_when_holdings_balanced():
    state = initialize_state()
    state["portfolio_input"] = [
        {"ticker": "AAPL", "shares": 1}, {"ticker": "MSFT", "shares": 1}, {"ticker": "GOOG", "shares": 1}
    ]
    state["question"] = "my portfolio"

    histories = {
        "AAPL": _history([100, 100, 100, 100, 100]),
        "MSFT": _history([100, 100, 100, 100, 100]),
        "GOOG": _history([100, 100, 100, 100, 100]),
    }
    with patch('app.agents.portfolio_analyst_agent.yf.Ticker', side_effect=_mock_ticker_side_effect(histories)):
        with patch('app.agents.portfolio_analyst_agent.get_llm') as mock_llm:
            mock_llm.return_value = MagicMock(invoke=MagicMock(
                return_value=MagicMock(content="Balanced.", model_used="m", fallback_used=False, degraded=None)
            ))
            result = _run(state)

    assert result["portfolio_analysis"]["concentrated_in"] is None


def test_concentration_flagged_when_one_holding_dominates():
    state = initialize_state()
    state["portfolio_input"] = [{"ticker": "AAPL", "shares": 100}, {"ticker": "MSFT", "shares": 1}]
    state["question"] = "my portfolio"

    histories = {
        "AAPL": _history([100, 100, 100, 100, 100]),
        "MSFT": _history([50, 50, 50, 50, 50]),
    }
    with patch('app.agents.portfolio_analyst_agent.yf.Ticker', side_effect=_mock_ticker_side_effect(histories)):
        with patch('app.agents.portfolio_analyst_agent.get_llm') as mock_llm:
            mock_llm.return_value = MagicMock(invoke=MagicMock(
                return_value=MagicMock(content="Concentrated.", model_used="m", fallback_used=False, degraded=None)
            ))
            result = _run(state)

    assert result["portfolio_analysis"]["concentrated_in"] == "AAPL"
