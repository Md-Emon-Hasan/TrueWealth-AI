from unittest.mock import MagicMock, patch

from app.agents.llm import query_llm
from app.core.state import initialize_state


def test_query_llm():
    state = initialize_state()
    state["question"] = "test"
    with patch('app.agents.llm.get_llm') as mock_llm:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "LLM Response"
        mock_llm.return_value = mock_instance
        result = query_llm(state)
        assert result["llm_attempted"] is True
        assert result["generation"] == "LLM Response"
