from unittest.mock import MagicMock, patch

from app.agents.rag import retrieve_docs
from app.core.state import initialize_state


def test_retrieve_docs():
    state = initialize_state()
    state["question"] = "test"
    with patch('app.agents.rag.get_retriever') as mock_retriever:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = ["Doc1"]
        mock_retriever.return_value = mock_instance
        result = retrieve_docs(state)
        assert result["rag_attempted"] is True
        assert result["documents"] == ["Doc1"]
