from unittest.mock import MagicMock, patch

from app.main import client_key


def test_client_key_uses_forwarded_for():
    request = MagicMock()
    request.headers = {"x-forwarded-for": "1.2.3.4, 5.6.7.8"}
    assert client_key(request) == "1.2.3.4"


def test_client_key_falls_back_to_remote_address():
    request = MagicMock()
    request.headers = {}
    with patch('app.main.get_remote_address', return_value="9.9.9.9"):
        assert client_key(request) == "9.9.9.9"


def test_rate_limiter_blocks_after_threshold():
    from fastapi import FastAPI, Request
    from fastapi.testclient import TestClient
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)
    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.get("/ping")
    @limiter.limit("2/minute")
    async def ping(request: Request):
        return {"ok": True}

    test_client = TestClient(app)
    assert test_client.get("/ping").status_code == 200
    assert test_client.get("/ping").status_code == 200
    assert test_client.get("/ping").status_code == 429
