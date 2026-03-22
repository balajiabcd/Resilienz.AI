"""
tests/api/conftest.py — Shared fixtures for API tests
"""

import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def client():
    """Create test client for the Flask app."""
    with patch("api.app.RAgent"):
        with patch("api.app.config") as mock_config:
            mock_config.SQLITE_DB_PATH = ":memory:"
            mock_config.FLASK_HOST = "0.0.0.0"
            mock_config.FLASK_PORT = 5000
            mock_config.FLASK_DEBUG = False

            import sys
            import os

            sys.path.insert(
                0,
                os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                ),
            )

            from api.app import app

            app.config["TESTING"] = True
            with app.test_client() as test_client:
                yield test_client
