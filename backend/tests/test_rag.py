from unittest.mock import MagicMock, patch

from app.agents.rag import retrieve_docs
from app.core.state import initialize_state


def test_retrieve_docs():
    state = initialize_state()
    state["question"] = "test"
    with patch('app.agents.rag.get_retriever') as mock_retriever:
        mock_instance = MagicMock()
        doc = MagicMock(page_content="Doc1")
        mock_instance.invoke.return_value = [doc]
        mock_retriever.return_value = mock_instance
        result = retrieve_docs(state)
        assert result["rag_attempted"] is True
        assert result["documents"][0].page_content == "Doc1"


def test_retrieve_docs_uses_cache_on_second_call():
    with patch('app.agents.rag.get_retriever') as mock_retriever:
        mock_instance = MagicMock()
        doc = MagicMock(page_content="Doc1")
        mock_instance.invoke.return_value = [doc]
        mock_retriever.return_value = mock_instance

        first = initialize_state()
        first["question"] = "cached query"
        retrieve_docs(first)

        second = initialize_state()
        second["question"] = "cached query"
        retrieve_docs(second)

        assert mock_retriever.call_count == 1
