from unittest.mock import MagicMock, patch

from app.agents.duckduckgo import retrieve_duckduckgo
from app.core.state import initialize_state


def test_retrieve_duckduckgo():
    state = initialize_state()
    state["question"] = "test"
    with patch('app.agents.duckduckgo.get_duckduckgo_search') as mock_search:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = "DDG Result"
        mock_search.return_value = mock_instance
        result = retrieve_duckduckgo(state)
        assert result["ddg_attempted"] is True
        assert result["source"] == "duckduckgo"
        assert "DDG Result" in result["documents"][0].page_content
