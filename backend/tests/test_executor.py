from app.agents.executor import executor
from app.core.state import initialize_state


def test_executor():
    # Test executor increment
    state = initialize_state()
    state["retry_count"] = 0
    result = executor(state)
    assert result["retry_count"] == 1
