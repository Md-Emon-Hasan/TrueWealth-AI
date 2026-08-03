from app.tools.llm_client import extract_tokens


class _Message:
    def __init__(self, response_metadata):
        self.response_metadata = response_metadata


def test_extract_tokens_reads_usage():
    message = _Message({"token_usage": {"total_tokens": 42}})
    assert extract_tokens(message) == 42


def test_extract_tokens_defaults_to_zero_when_missing_usage():
    message = _Message({})
    assert extract_tokens(message) == 0


def test_extract_tokens_handles_missing_response_metadata():
    class NoMetadata:
        pass

    assert extract_tokens(NoMetadata()) == 0
