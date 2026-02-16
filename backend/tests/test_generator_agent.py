from unittest.mock import MagicMock, patch

from app.agents.generator import generate_response
from app.core.state import initialize_state


def test_generate_response():
    # Test generation from documents
    state = initialize_state()
    state["source"] = "rag_documents"
    state["documents"] = [MagicMock(page_content="Context")]
    state["question"] = "test"
    with patch('app.agents.generator.get_llm') as mock_llm:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "Generated"
        mock_llm.return_value = mock_instance
        result = generate_response(state)
        assert result["generation"] == "Generated"

    # Test llm_knowledge source (early return)
    state = initialize_state()
    state["source"] = "llm_knowledge"
    result = generate_response(state)
    assert result["source"] == "llm_knowledge"

    # Test fallback (no documents)
    state = initialize_state()
    state["source"] = "rag_documents"
    state["documents"] = []
    result = generate_response(state)
    assert "couldn't find enough financial data" in result["generation"]
