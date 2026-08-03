import logging
from unittest.mock import patch

from app.core.logger import setup_logger


def test_setup_logger_skips_duplicate_handlers():
    with patch('app.core.logger.logging.FileHandler') as mock_handler:
        mock_handler.return_value = logging.StreamHandler()
        first = setup_logger("test_logger_dup")
        second = setup_logger("test_logger_dup")
    assert first is second
    assert len(first.handlers) == 2


def test_setup_logger_creates_missing_logs_dir():
    with patch('app.core.logger.os.path.exists', return_value=False):
        with patch('app.core.logger.os.makedirs') as mock_makedirs:
            with patch('app.core.logger.logging.FileHandler') as mock_handler:
                mock_handler.return_value = logging.StreamHandler()
                setup_logger("test_logger_newdir")
                mock_makedirs.assert_called_once()
