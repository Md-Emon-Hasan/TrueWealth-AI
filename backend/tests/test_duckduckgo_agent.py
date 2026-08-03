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
        assert result["degraded"] == ""


def test_retrieve_duckduckgo_empty_result_is_degraded():
    state = initialize_state()
    state["question"] = "obscure query"
    with patch('app.agents.duckduckgo.get_duckduckgo_search') as mock_search:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = "   "
        mock_search.return_value = mock_instance
        result = retrieve_duckduckgo(state)
        assert result["documents"] == []
        assert result["degraded"] == "duckduckgo_no_data"


def test_retrieve_duckduckgo_error_is_degraded():
    state = initialize_state()
    state["question"] = "test"
    with patch('app.agents.duckduckgo.get_duckduckgo_search') as mock_search:
        mock_instance = MagicMock()
        mock_instance.invoke.side_effect = Exception("rate limited")
        mock_search.return_value = mock_instance
        result = retrieve_duckduckgo(state)
        assert result["documents"] == []
        assert result["degraded"] == "duckduckgo_unavailable"


def test_retrieve_duckduckgo_uses_cache_on_second_call():
    state = initialize_state()
    state["question"] = "test"
    with patch('app.agents.duckduckgo.get_duckduckgo_search') as mock_search:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = "cached result"
        mock_search.return_value = mock_instance
        retrieve_duckduckgo(dict(state))
        retrieve_duckduckgo(dict(state))
        assert mock_instance.invoke.call_count == 1
