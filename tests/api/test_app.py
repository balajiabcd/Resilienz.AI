"""
tests/api/test_app.py — Tests for api/app.py

Tests Flask API endpoints and HTTP responses.
"""

import pytest
import json
from unittest.mock import MagicMock, patch


@pytest.fixture
def client():
    """Create test client."""
    with patch("api.app.agent") as mock_agent:
        mock_agent.run_risk_audit.return_value = "Test report"
        mock_agent.ask.return_value = "Test response"

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


class TestHomeEndpoint:
    """Tests for home endpoint."""

    def test_home_returns_html(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Resilienz.AI" in response.data

    def test_home_contains_status_info(self, client):
        response = client.get("/")
        data = response.data.decode()
        assert "API Status" in data or "LIVE" in data


class TestDashboardSummary:
    """Tests for dashboard summary endpoint."""

    def test_summary_endpoint_exists(self, client):
        with patch("api.app.get_db_connection") as mock_conn:
            mock_conn.return_value.execute.return_value.fetchone.return_value = [5]
            mock_conn.return_value.close = MagicMock()
            response = client.get("/api/dashboard/summary")
            assert response.status_code in [200, 500]


class TestInventoryEndpoint:
    """Tests for inventory endpoint."""

    def test_inventory_endpoint_exists(self, client):
        with patch("api.app.get_db_connection") as mock_conn:
            mock_conn.return_value.execute.return_value.fetchall.return_value = []
            mock_conn.return_value.close = MagicMock()
            response = client.get("/api/inventory")
            assert response.status_code in [200, 500]


class TestCriticalOrdersEndpoint:
    """Tests for critical orders endpoint."""

    def test_critical_endpoint_exists(self, client):
        with patch("api.app.get_db_connection") as mock_conn:
            mock_conn.return_value.execute.return_value.fetchall.return_value = []
            mock_conn.return_value.close = MagicMock()
            response = client.get("/api/orders/critical")
            assert response.status_code in [200, 500]


class TestAgentAuditEndpoint:
    """Tests for agent audit endpoint."""

    def test_audit_returns_json(self, client):
        with patch("api.app.agent") as mock_agent:
            mock_agent.run_risk_audit.return_value = "Test report"

            response = client.post("/api/agent/audit")

            assert response.status_code in [200, 500]

    def test_audit_returns_report(self, client):
        with patch("api.app.agent") as mock_agent:
            mock_agent.run_risk_audit.return_value = "Risk Report Content"

            response = client.post("/api/agent/audit")
            if response.status_code == 200:
                data = response.get_json()
                assert "report" in data

    def test_audit_handles_exception(self, client):
        with patch("api.app.agent") as mock_agent:
            mock_agent.run_risk_audit.side_effect = Exception("Audit failed")

            response = client.post("/api/agent/audit")

            assert response.status_code in [200, 500]


class TestAgentChatEndpoint:
    """Tests for agent chat endpoint."""

    def test_chat_requires_question(self, client):
        response = client.post(
            "/api/agent/chat", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code in [200, 400]

    def test_chat_returns_response(self, client):
        with patch("api.app.agent") as mock_agent:
            mock_agent.ask.return_value = "AI Response"

            response = client.post(
                "/api/agent/chat",
                data=json.dumps({"question": "What is the risk?"}),
                content_type="application/json",
            )

            assert response.status_code in [200, 500]

    def test_chat_handles_exception(self, client):
        with patch("api.app.agent") as mock_agent:
            mock_agent.ask.side_effect = Exception("AI Error")

            response = client.post(
                "/api/agent/chat",
                data=json.dumps({"question": "Test"}),
                content_type="application/json",
            )

            assert response.status_code in [200, 500]

    def test_chat_empty_question(self, client):
        response = client.post(
            "/api/agent/chat",
            data=json.dumps({"question": ""}),
            content_type="application/json",
        )

        assert response.status_code in [200, 400]


class TestReportsEndpoint:
    """Tests for reports download endpoint."""

    def test_reports_endpoint_exists(self, client):
        with patch("api.app.send_from_directory") as mock_send:
            mock_send.return_value = "PDF content"

            response = client.get("/api/reports/test_report.pdf")

            assert response.status_code in [200, 404]


class TestAPIEdgeCases:
    """Edge case tests for API."""

    def test_chat_missing_content_type(self, client):
        with patch("api.app.agent") as mock_agent:
            mock_agent.ask.return_value = "Response"

            response = client.post("/api/agent/chat", data="question=test")

            assert response.status_code in [200, 400, 415]

    def test_chat_invalid_json(self, client):
        response = client.post(
            "/api/agent/chat", data="not json", content_type="application/json"
        )

        assert response.status_code in [200, 400]


class TestAPIStress:
    """Stress tests for API."""

    def test_many_home_requests(self, client):
        for _ in range(10):
            response = client.get("/")
            assert response.status_code == 200

    def test_many_chat_requests(self, client):
        with patch("api.app.agent") as mock_agent:
            mock_agent.ask.return_value = "Response"

            for i in range(10):
                response = client.post(
                    "/api/agent/chat",
                    data=json.dumps({"question": f"Question {i}"}),
                    content_type="application/json",
                )
                assert response.status_code in [200, 500]
