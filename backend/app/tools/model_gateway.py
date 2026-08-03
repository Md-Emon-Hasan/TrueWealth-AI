import litellm
from cachetools import TTLCache

from app.core.config import (GATEWAY_CACHE_TTL, GATEWAY_RETRY_LIMIT,
                             MODEL_ANSWER, MODEL_CLASSIFY, MODEL_REASONING)
from app.core.logger import logger

# each tier falls back to the next-cheaper Groq model on rate limits, never to another provider
TIER_CHAINS = {
    "answer": [MODEL_ANSWER, MODEL_REASONING, MODEL_CLASSIFY],
    "reasoning": [MODEL_REASONING, MODEL_CLASSIFY],
    "classify": [MODEL_CLASSIFY],
}

_response_cache = TTLCache(maxsize=256, ttl=GATEWAY_CACHE_TTL)


class GatewayMessage:
    def __init__(self, content, model_used, fallback_used, degraded, tokens_used):
        self.content = content
        self.model_used = model_used
        self.fallback_used = fallback_used
        self.degraded = degraded
        self.response_metadata = {"token_usage": {"total_tokens": tokens_used}}


def _call_model(model_id, prompt, retries):
    last_error = None
    for _ in range(retries + 1):
        try:
            return litellm.completion(
                model=f"groq/{model_id}",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
        except litellm.RateLimitError as e:
            raise e
        except Exception as e:
            last_error = e
    raise last_error


class Gateway:
    def __init__(self, tier):
        self.tier = tier

    def invoke(self, prompt):
        chain = TIER_CHAINS[self.tier]
        for i, model_id in enumerate(chain):
            try:
                response = _call_model(model_id, prompt, retries=GATEWAY_RETRY_LIMIT)
                tokens = getattr(getattr(response, "usage", None), "total_tokens", 0) or 0
                content = response.choices[0].message.content
                _response_cache[prompt] = content
                return GatewayMessage(content, model_id, i > 0, None, tokens)
            except litellm.RateLimitError:
                logger.info(f"model_gateway: {model_id} rate limited, dropping a tier")
            except Exception as e:
                logger.error(f"model_gateway: {model_id} failed: {e}")

        cached = _response_cache.get(prompt)
        if cached is not None:
            return GatewayMessage(cached, "cache", True, "model_gateway_cache_fallback", 0)

        return GatewayMessage(
            "I'm temporarily unable to reach the language model. Please try again shortly.",
            None, True, "model_gateway_exhausted", 0
        )


def get_llm(tier="answer"):
    return Gateway(tier)
