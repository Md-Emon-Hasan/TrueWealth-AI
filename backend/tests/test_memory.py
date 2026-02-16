from app.agents.memory import recall_memory, store_memory
from app.core.state import initialize_state


def test_memory_store_and_recall():
    state = initialize_state()
    state["conversation_history"] = ["Hello", "Hi"]

    # Test store
    state = store_memory(state)
    assert state["memory"] == ["Hello", "Hi"]

    # Test recall
    state["conversation_history"] = []
    state = recall_memory(state)
    assert state["conversation_history"] == ["Hello", "Hi"]
