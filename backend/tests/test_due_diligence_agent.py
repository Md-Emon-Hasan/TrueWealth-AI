from unittest.mock import MagicMock, patch

from app.agents.due_diligence_agent import _parse_verdict, due_diligence_agent
from app.core.state import initialize_state


def _doc(text):
    return MagicMock(page_content=text)


def test_skips_llm_when_rag_answer_is_clean():
    state = initialize_state()
    state["question"] = "what does the book say about risk"
    state["generation"] = "Graham stresses discipline over speculation."
    state["source"] = "rag_documents"
    state["documents"] = [_doc("Graham stresses discipline over speculation.")]

    with patch('app.agents.due_diligence_agent.get_llm') as mock_llm:
        result = due_diligence_agent(state)
        mock_llm.assert_not_called()

    assert result["verification"]["risk"] == "low"
    assert result["verification"]["revised"] is False


def test_skips_llm_when_llm_knowledge_has_no_figures():
    state = initialize_state()
    state["generation"] = "Diversification spreads risk across assets."
    state["source"] = "llm_knowledge"
    state["documents"] = []

    with patch('app.agents.due_diligence_agent.get_llm') as mock_llm:
        result = due_diligence_agent(state)
        mock_llm.assert_not_called()

    assert result["verification"]["risk"] == "low"


def test_flags_figure_absent_from_evidence():
    state = initialize_state()
    state["generation"] = "The fund returned 42% last year."
    state["source"] = "rag_documents"
    state["documents"] = [_doc("The fund's strategy focuses on value investing.")]

    with patch('app.agents.due_diligence_agent.get_llm') as mock_llm:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(
            content='{"grounded": false, "citations_valid": true, "unsupported_figures": ["42%"], '
                    '"needs_revision": false, "risk": "high"}',
            degraded=None
        )
        mock_llm.return_value = mock_instance
        result = due_diligence_agent(state)

    assert "42%" in result["verification"]["unsupported_figures"]
    assert result["verification"]["risk"] == "high"


def test_llm_knowledge_with_figure_is_not_clean():
    state = initialize_state()
    state["generation"] = "The S&P 500 returned 8% last year."
    state["source"] = "llm_knowledge"
    state["documents"] = []

    with patch('app.agents.due_diligence_agent.get_llm') as mock_llm:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(
            content='{"grounded": false, "citations_valid": true, "unsupported_figures": ["8%"], '
                    '"needs_revision": true, "risk": "medium"}',
            degraded=None
        )
        mock_llm.return_value = mock_instance
        result = due_diligence_agent(state)
        assert mock_instance.invoke.call_count == 2

    assert result["verification"]["revised"] is True


def test_falls_back_to_pre_check_on_unparseable_critique():
    state = initialize_state()
    state["generation"] = "The fund returned 42% last year."
    state["source"] = "rag_documents"
    state["documents"] = [_doc("no numbers here")]

    with patch('app.agents.due_diligence_agent.get_llm') as mock_llm:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="not json", degraded=None)
        mock_llm.return_value = mock_instance
        result = due_diligence_agent(state)

    assert result["verification"]["risk"] == "high"
    assert result["degraded"] == "due_diligence_critique_unparseable"


def test_parse_verdict_strips_markdown_fence():
    fenced = '```json\n{"grounded": true, "citations_valid": true, "unsupported_figures": [], ' \
             '"needs_revision": false, "risk": "low"}\n```'
    verdict = _parse_verdict(fenced)
    assert verdict["risk"] == "low"


def test_gateway_degradation_propagates():
    state = initialize_state()
    state["generation"] = "The fund returned 42% last year."
    state["source"] = "rag_documents"
    state["documents"] = [_doc("no numbers here")]

    with patch('app.agents.due_diligence_agent.get_llm') as mock_llm:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="unparseable", degraded="model_gateway_exhausted")
        mock_llm.return_value = mock_instance
        result = due_diligence_agent(state)

    assert result["degraded"] == "model_gateway_exhausted"
