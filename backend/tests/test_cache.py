from app.core.cache import (cache_get, cache_set, rag_cache,
                             used_live_market_data)


def test_cache_get_set_roundtrip():
    cache_set(rag_cache, "k", "v")
    assert cache_get(rag_cache, "k") == "v"


def test_cache_miss_returns_none():
    assert cache_get(rag_cache, "missing") is None


def test_used_live_market_data_true_for_yfinance():
    assert used_live_market_data("yfinance") is True


def test_used_live_market_data_true_for_market_desk_and_portfolio():
    assert used_live_market_data("market_desk") is True
    assert used_live_market_data("portfolio_analysis") is True


def test_used_live_market_data_false_for_other_sources():
    assert used_live_market_data("rag_documents") is False
    assert used_live_market_data("llm_knowledge") is False
    assert used_live_market_data("duckduckgo") is False
