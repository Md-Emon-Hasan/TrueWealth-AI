from unittest.mock import MagicMock, patch

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


def test_recall_rehydrates_from_db_when_memory_empty():
    state = initialize_state()
    state["session_id"] = "s1"
    row = MagicMock(question="what is a bond", answer="a debt security")
    with patch('app.core.db.get_session_history', return_value=[row]):
        result = recall_memory(state)
    assert "Client: what is a bond" in result["conversation_history"]
    assert "Advisor: a debt security" in result["conversation_history"]


def test_recall_skips_rehydrate_when_memory_present():
    state = initialize_state()
    state["memory"] = ["Client: x", "Advisor: y"]
    state["session_id"] = "s1"
    with patch('app.core.db.get_session_history') as mock_history:
        recall_memory(state)
        mock_history.assert_not_called()


def test_recall_prepends_semantic_matches():
    state = initialize_state()
    state["question"] = "what did we discuss about bonds"
    state["session_id"] = "s1"
    doc = MagicMock(page_content="Client: old bond question\nAdvisor: old bond answer")
    with patch('app.agents.memory.get_memory_store') as mock_store:
        mock_store.return_value.similarity_search.return_value = [doc]
        result = recall_memory(state)
    assert "Client: old bond question\nAdvisor: old bond answer" in result["conversation_history"]


def test_recall_semantic_degrades_gracefully_on_error():
    state = initialize_state()
    state["question"] = "what is a bond"
    with patch('app.agents.memory.get_memory_store', side_effect=Exception("chroma down")):
        result = recall_memory(state)
    assert result["conversation_history"] == []


def test_store_semantic_memory_adds_exchange():
    state = initialize_state()
    state["question"] = "what is a bond"
    state["generation"] = "a debt security"
    state["session_id"] = "s1"
    with patch('app.agents.memory.get_memory_store') as mock_store:
        store_memory(state)
        mock_store.return_value.add_texts.assert_called_once()


def test_store_semantic_memory_skips_when_no_generation():
    state = initialize_state()
    state["question"] = "what is a bond"
    with patch('app.agents.memory.get_memory_store') as mock_store:
        store_memory(state)
        mock_store.assert_not_called()


def test_store_semantic_memory_degrades_gracefully_on_error():
    state = initialize_state()
    state["question"] = "what is a bond"
    state["generation"] = "a debt security"
    with patch('app.agents.memory.get_memory_store', side_effect=Exception("chroma down")):
        result = store_memory(state)
    assert result["memory"] == []
