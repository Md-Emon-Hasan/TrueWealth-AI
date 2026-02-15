import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import sys
import os

# Mock dependencies that might be missing in the environment
sys.modules["core"] = MagicMock()
sys.modules["core.workflow"] = MagicMock()
sys.modules["core.state"] = MagicMock()
sys.modules["langchain_core"] = MagicMock()
sys.modules["langchain_core.documents"] = MagicMock()

# Add backend to path so we can import app.main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_workflow():
    with patch('app.main.ai_workflow') as mock:
        yield mock

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
