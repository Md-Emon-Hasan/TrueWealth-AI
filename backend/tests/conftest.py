import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["SQLITE_PATH"] = os.path.join(tempfile.gettempdir(), "truewealth_test.sqlite3")


# Mock dependencies that might be missing in the environment
def mock_package(name):
    mock = MagicMock()
    sys.modules[name] = mock
    return mock


# Aggressively mock all external AI packages
def mock_ai_stuff():
    packages = [
        "langchain_core", "langchain_core.documents", "langchain_core.messages", "langchain_core.prompts",
        "langchain_core.runnables", "langchain_groq", "langchain", "langchain_community", "langchain_community.tools",
        "langchain_community.tools.ddg_search", "langchain_community.tools.ddg_search.tool",
        "langchain_community.tools.yahoo_finance_news", "langchain_community.document_loaders",
        "langchain_community.vectorstores", "langgraph", "langgraph.graph", "langchain_huggingface",
        "langchain_huggingface.embeddings", "langchain_text_splitters", "langchain_chroma",
        "chromadb", "sentence_transformers", "huggingface_hub", "tiktoken", "pypdf",
        "wikipedia", "duckduckgo_search", "yahoo_finance", "langchain_openai", "langchain_anthropic"
    ]
    for pkg in packages:
        # Create mocks for all parent packages too
        parts = pkg.split('.')
        for i in range(1, len(parts) + 1):
            parent = '.'.join(parts[:i])
            if parent.startswith('app'):
                continue
            if parent not in sys.modules:
                m = MagicMock()
                if i < len(parts):  # If it's a parent, it must have a __path__
                    m.__path__ = []
                sys.modules[parent] = m


mock_ai_stuff()


# Provide a realistic mock for langchain_core.documents.Document
class MockDocument:
    def __init__(self, page_content="", metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

    def __repr__(self):
        return f"Document(page_content='{self.page_content}')"


sys.modules["langchain_core.documents"].Document = MockDocument

# Add backend to path so we can import app.main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
def mock_workflow():
    with patch('app.main.ai_workflow') as mock:
        yield mock


@pytest.fixture(autouse=True)
def clear_caches():
    from app.core import cache
    from app.tools import model_gateway
    for c in (cache.embedding_cache, cache.rag_cache, cache.market_quote_cache,
              cache.news_cache, cache.ddg_cache, cache.answer_cache,
              model_gateway._response_cache):
        c.clear()
    yield


@pytest.fixture
def mock_initialize_state():
    with patch('app.main.initialize_state') as mock:
        mock.return_value = {
            "question": "",
            "generation": "",
            "documents": [],
            "source": "",
            "retry_count": 0
        }
        yield mock
