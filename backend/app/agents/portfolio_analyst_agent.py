import asyncio
import re

import numpy as np
import pandas as pd
import yfinance as yf
from app.core.config import (PORTFOLIO_CONCENTRATION_THRESHOLD_PCT,
                             PORTFOLIO_HISTORY_PERIOD)
from app.core.state import AgentState
from app.tools.llm_client import extract_tokens
from app.tools.model_gateway import get_llm
from langchain_core.documents import Document

_HOLDING_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s+shares?\s+of\s+([A-Za-z]{1,5})\b", re.I)

EXPLAIN_PROMPT = """You are a financial advisor explaining a client's portfolio analysis in plain language.

Computed metrics:
{summary}

Respond in 2-3 professional, concise sentences covering allocation, risk, and any concentration concern. \
Do not invent numbers beyond what is given above."""


def _parse_holdings_from_text(question):
    return [{"ticker": m.group(2).upper(), "shares": float(m.group(1))} for m in _HOLDING_PATTERN.finditer(question)]


def _fetch_ticker_history(ticker):
    try:
        history = yf.Ticker(ticker).history(period=PORTFOLIO_HISTORY_PERIOD)
    except Exception:
        return ticker, None
    if history is None or history.empty:
        return ticker, None
    return ticker, history["Close"]


async def _fetch_all_histories(tickers):
    results = await asyncio.gather(*(asyncio.to_thread(_fetch_ticker_history, t) for t in tickers))
    return dict(results)


def _compute_metrics(holdings, closes):
    shares = pd.Series({h["ticker"]: h["shares"] for h in holdings if h["ticker"] in closes})
    combined = pd.concat({t: closes[t] for t in shares.index}, axis=1).dropna()

    latest_prices = combined.iloc[-1]
    values = latest_prices * shares
    total_value = values.sum()
    allocation_pct = (values / total_value * 100).round(2).to_dict()

    portfolio_value = (combined * shares).sum(axis=1)
    returns = portfolio_value.pct_change().dropna()
    volatility_pct = round(float(returns.std() * np.sqrt(252) * 100), 2) if len(returns) > 1 else 0.0

    running_max = portfolio_value.cummax()
    drawdown = (portfolio_value - running_max) / running_max
    max_drawdown_pct = round(float(drawdown.min() * 100), 2) if len(drawdown) else 0.0

    top_ticker = max(allocation_pct, key=allocation_pct.get)
    concentrated = allocation_pct[top_ticker] >= PORTFOLIO_CONCENTRATION_THRESHOLD_PCT

    return {
        "total_value": round(float(total_value), 2),
        "allocation_pct": allocation_pct,
        "volatility_annualized_pct": volatility_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "concentrated_in": top_ticker if concentrated else None,
    }


async def portfolio_analyst_agent(state: AgentState):
    """Computes real allocation/volatility/drawdown from holdings via pandas/numpy, then explains them"""
    holdings = state.get('portfolio_input') or _parse_holdings_from_text(state['question'])

    if not holdings:
        state['generation'] = (
            "I couldn't identify your holdings from that message. Please list them like "
            "\"10 shares of AAPL and 5 shares of MSFT\", or pass a structured portfolio field."
        )
        state['source'] = 'portfolio_analysis'
        state['degraded'] = 'portfolio_not_parsed'
        state['documents'] = []
        return state

    tickers = [h["ticker"] for h in holdings]
    closes = await _fetch_all_histories(tickers)
    valid_closes = {t: c for t, c in closes.items() if c is not None}
    missing = [t for t in tickers if t not in valid_closes]

    if not valid_closes:
        state['generation'] = "I couldn't retrieve market data for any of the listed holdings right now."
        state['source'] = 'portfolio_analysis'
        state['degraded'] = 'portfolio_data_unavailable'
        state['documents'] = []
        return state

    metrics = _compute_metrics(holdings, valid_closes)
    summary_lines = [
        f"Total portfolio value: ${metrics['total_value']:,}",
        f"Allocation: {metrics['allocation_pct']}",
        f"Annualized volatility: {metrics['volatility_annualized_pct']}%",
        f"Max drawdown over {PORTFOLIO_HISTORY_PERIOD}: {metrics['max_drawdown_pct']}%",
    ]
    if metrics['concentrated_in']:
        summary_lines.append(
            f"Concentration risk: {metrics['concentrated_in']} exceeds "
            f"{PORTFOLIO_CONCENTRATION_THRESHOLD_PCT}% of the portfolio"
        )
    if missing:
        summary_lines.append(f"Data unavailable for: {', '.join(missing)}")
    summary_text = "\n".join(summary_lines)

    llm = get_llm("answer")
    message = llm.invoke(EXPLAIN_PROMPT.format(summary=summary_text))

    state['generation'] = message.content.strip()
    state['tokens_used'] = state.get('tokens_used', 0) + extract_tokens(message)
    state['model_used'] = message.model_used or state.get('model_used', '')
    state['fallback_used'] = state.get('fallback_used', False) or message.fallback_used
    state['degraded'] = message.degraded or (f"portfolio_data_missing:{','.join(missing)}" if missing else '')
    state['source'] = 'portfolio_analysis'
    state['documents'] = [Document(page_content=summary_text)]
    state['portfolio_analysis'] = metrics

    return state
