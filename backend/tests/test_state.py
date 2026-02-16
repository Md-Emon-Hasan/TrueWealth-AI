from app.core.state import initialize_state


def test_initialize_state():
    state = initialize_state()
    assert state["question"] == ""
    assert state["retry_count"] == 0
    assert isinstance(state["memory"], list)
