from unittest.mock import MagicMock, patch

import litellm

from app.tools.model_gateway import get_llm


def _fake_response(text, tokens=10):
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=text))]
    response.usage = MagicMock(total_tokens=tokens)
    return response


def test_gateway_uses_primary_model():
    with patch('app.tools.model_gateway.litellm.completion') as mock_completion:
        mock_completion.return_value = _fake_response("hello")
        message = get_llm("answer").invoke("hi")

        assert message.content == "hello"
        assert message.model_used == "openai/gpt-oss-120b"
        assert message.fallback_used is False
        assert message.degraded is None


def test_gateway_drops_tier_on_rate_limit():
    with patch('app.tools.model_gateway.litellm.completion') as mock_completion:
        mock_completion.side_effect = [
            litellm.RateLimitError("rate limited", llm_provider="groq", model="openai/gpt-oss-120b"),
            _fake_response("fallback answer"),
        ]
        message = get_llm("answer").invoke("hi there")

        assert message.content == "fallback answer"
        assert message.model_used == "llama-3.3-70b-versatile"
        assert message.fallback_used is True


def test_gateway_falls_back_to_cache_after_exhaustion():
    with patch('app.tools.model_gateway.litellm.completion') as mock_completion:
        mock_completion.return_value = _fake_response("first answer")
        get_llm("classify").invoke("repeat me")

    with patch('app.tools.model_gateway.litellm.completion') as mock_completion:
        mock_completion.side_effect = Exception("groq down")
        message = get_llm("classify").invoke("repeat me")

        assert message.content == "first answer"
        assert message.degraded == "model_gateway_cache_fallback"


def test_gateway_returns_explicit_degraded_response_when_exhausted():
    with patch('app.tools.model_gateway.litellm.completion') as mock_completion:
        mock_completion.side_effect = Exception("groq down")
        message = get_llm("classify").invoke("never asked before")

        assert message.degraded == "model_gateway_exhausted"
        assert message.model_used is None


def test_gateway_tier_chains_differ():
    from app.tools.model_gateway import TIER_CHAINS
    assert len(TIER_CHAINS["answer"]) == 3
    assert len(TIER_CHAINS["classify"]) == 1
