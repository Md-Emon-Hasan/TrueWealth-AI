from app.core.workflow import decide_next_step, route_intent


def test_decide_next_step_success():
    state = {"llm_attempted": True, "generation": "I can help with that."}
    assert decide_next_step(state) == "due_diligence_agent"


def test_decide_next_step_rag():
    state = {"llm_attempted": True, "generation": "I don't know", "retry_count": 0}
    assert decide_next_step(state) == "retrieve_docs"


def test_decide_next_step_yfinance():
    state = {"llm_attempted": True, "generation": "I don't know", "retry_count": 1}
    assert decide_next_step(state) == "retrieve_yfinance"


def test_decide_next_step_ddg():
    state = {"llm_attempted": True, "generation": "I don't know", "retry_count": 2}
    assert decide_next_step(state) == "retrieve_duckduckgo"


def test_decide_next_step_fallback():
    state = {"llm_attempted": True, "generation": "I don't know", "retry_count": 3}
    assert decide_next_step(state) == "generate_response"


def test_decide_next_step_initial():
    state = {"llm_attempted": False, "retry_count": 0}
    assert decide_next_step(state) == "retrieve_docs"


def test_route_intent_portfolio_keyword():
    state = {"question": "what's my portfolio allocation looking like"}
    assert route_intent(state) == "portfolio_analyst_agent"


def test_route_intent_structured_portfolio_input():
    state = {"question": "how am I doing", "portfolio_input": [{"ticker": "AAPL", "shares": 1}]}
    assert route_intent(state) == "portfolio_analyst_agent"


def test_route_intent_market_keyword():
    state = {"question": "what's the current price of gold"}
    assert route_intent(state) == "market_desk_agent"


def test_route_intent_ticker_like_token():
    state = {"question": "any updates on TSLA"}
    assert route_intent(state) == "market_desk_agent"


def test_route_intent_general_question():
    state = {"question": "what is diversification"}
    assert route_intent(state) == "query_llm"
