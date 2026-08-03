import os
import threading

from cachetools import TTLCache

from app.core.config import (ANSWER_CACHE_TTL, CACHE_MAXSIZE, DB_DIR,
                             DDG_CACHE_TTL, EMBEDDING_CACHE_TTL,
                             MARKET_QUOTE_CACHE_TTL, NEWS_CACHE_TTL,
                             RAG_CACHE_TTL)

_lock = threading.Lock()

embedding_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=EMBEDDING_CACHE_TTL)
rag_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=RAG_CACHE_TTL)
market_quote_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=MARKET_QUOTE_CACHE_TTL)
news_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=NEWS_CACHE_TTL)
ddg_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=DDG_CACHE_TTL)
answer_cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=ANSWER_CACHE_TTL)


def cache_get(cache, key):
    with _lock:
        return cache.get(key)


def cache_set(cache, key, value):
    with _lock:
        cache[key] = value


def _index_version():
    sqlite_file = os.path.join(DB_DIR, "chroma.sqlite3")
    return os.path.getmtime(sqlite_file) if os.path.exists(sqlite_file) else 0


RAG_INDEX_VERSION = _index_version()


def used_live_market_data(source):
    return source == "yfinance"
