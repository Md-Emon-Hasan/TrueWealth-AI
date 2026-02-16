from app.core.workflow import decide_next_step


def test_decide_next_step_success():
    state = {"llm_attempted": True, "generation": "I can help with that."}
    assert decide_next_step(state) == "store_memory"


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
