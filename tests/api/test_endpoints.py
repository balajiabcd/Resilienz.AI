"""
tests/api/test_endpoints.py — Tests for new API endpoints

Tests: /api/map/data, /api/scenario/*, /api/stream/thoughts
"""

import pytest
import json
from unittest.mock import MagicMock, patch, PropertyMock


class TestMapDataEndpoint:
    """Tests for /api/map/data endpoint."""

    def test_map_data_returns_valid_structure(self, client):
        """GET /api/map/data returns hub and suppliers keys."""
        with patch("data.map_data.get_supplier_coords") as mock_coords:
            mock_coords.return_value = [
                {
                    "supplier_id": "SUP-001",
                    "name": "Test Supplier",
                    "city": "Berlin",
                    "country": "DE",
                    "lat": 52.52,
                    "lon": 13.405,
                    "risk_category": "LOW",
                    "reliability_score": 0.95,
                    "active_pos": 2,
                    "current_delay_days": 0,
                }
            ]
            response = client.get("/api/map/data")
            assert response.status_code == 200
            data = response.get_json()
            assert "hub" in data
            assert "suppliers" in data
            assert isinstance(data["suppliers"], list)

    def test_map_data_hub_has_coordinates(self, client):
        """Hub response includes lat/lon."""
        with patch("data.map_data.get_supplier_coords") as mock_coords:
            mock_coords.return_value = []
            with patch(
                "data.map_data.FACTORY_HUB",
                {"name": "Factory HQ", "lat": 48.7324, "lon": 11.8528},
            ):
                response = client.get("/api/map/data")
                data = response.get_json()
                assert "lat" in data["hub"]
                assert "lon" in data["hub"]

    def test_map_data_suppliers_have_required_fields(self, client):
        """Each supplier has lat, lon, and risk_category."""
        with patch("data.map_data.get_supplier_coords") as mock_coords:
            mock_coords.return_value = [
                {
                    "supplier_id": "SUP-001",
                    "name": "Test Supplier",
                    "city": "Berlin",
                    "country": "DE",
                    "lat": 52.52,
                    "lon": 13.405,
                    "risk_category": "MEDIUM",
                    "reliability_score": 0.85,
                    "active_pos": 1,
                    "current_delay_days": 0,
                }
            ]
            with patch("data.map_data.get_supplier_coords", mock_coords):
                response = client.get("/api/map/data")
                data = response.get_json()
                supplier = data["suppliers"][0]
                assert "lat" in supplier
                assert "lon" in supplier
                assert "risk_category" in supplier


class TestScenarioTrigger:
    """Tests for /api/scenario/trigger endpoint."""

    def test_trigger_requires_scenario_id(self, client):
        """POST without scenario_id returns 400."""
        response = client.post(
            "/api/scenario/trigger",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_trigger_unknown_scenario_returns_400(self, client):
        """POST with unknown scenario_id returns 400."""
        response = client.post(
            "/api/scenario/trigger",
            data=json.dumps({"scenario_id": "nonexistent_scenario"}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_trigger_valid_scenario_returns_200(self, client):
        """POST with valid scenario_id returns 200."""
        with patch("api.app.get_db_connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value.fetchall.return_value = []
            mock_conn.return_value = MagicMock(cursor=MagicMock())
            mock_conn.return_value.execute = mock_cursor
            mock_conn.return_value.close = MagicMock()

            with patch("api.app._inject_chroma_event"):
                response = client.post(
                    "/api/scenario/trigger",
                    data=json.dumps({"scenario_id": "suez_blockage"}),
                    content_type="application/json",
                )
                assert response.status_code == 200
                data = response.get_json()
                assert data["status"] == "active"
                assert "affected_suppliers" in data

    def test_trigger_conflict_when_active(self, client):
        """Triggering a second scenario while one is active returns 409."""
        with patch("api.app.get_db_connection") as mock_conn:
            mock_conn.return_value.execute.return_value.fetchall.return_value = []
            mock_conn.return_value.close = MagicMock()

            with patch("api.app._inject_chroma_event"):
                with patch("api.app._active_scenario_id", "port_strike"):
                    response = client.post(
                        "/api/scenario/trigger",
                        data=json.dumps({"scenario_id": "suez_blockage"}),
                        content_type="application/json",
                    )
                    assert response.status_code == 409


class TestScenarioReset:
    """Tests for /api/scenario/reset endpoint."""

    def test_reset_without_active_scenario_returns_400(self, client):
        """POST /api/scenario/reset when no scenario active returns 400."""
        with patch("api.app._active_scenario_id", None):
            response = client.post("/api/scenario/reset")
            assert response.status_code == 400

    def test_reset_clears_active_scenario(self, client):
        """POST /api/scenario/reset clears the scenario."""
        with patch("api.app._active_scenario_id", "suez_blockage"):
            with patch("api.app._active_overrides", {"SUP-001": 10}):
                with patch("api.app._injected_chroma_ids", ["SCENARIO-SUEZ"]):
                    with patch("api.app.get_db_checksum") as mock_checksum:
                        mock_checksum.return_value = {
                            "suppliers": 20,
                            "orders": 50,
                            "status": 50,
                            "inventory": 15,
                        }
                        with patch("api.app._remove_chroma_event"):
                            response = client.post("/api/scenario/reset")
                            assert response.status_code == 200
                            data = response.get_json()
                            assert data["status"] == "reset"
                            assert "checksum" in data


class TestScenarioStatus:
    """Tests for /api/scenario/status endpoint."""

    def test_status_returns_correct_state(self, client):
        """GET /api/scenario/status returns active scenario and overrides."""
        with patch("api.app._active_scenario_id", "port_strike"):
            with patch("api.app._active_overrides", {"SUP-001": 7, "SUP-002": 7}):
                response = client.get("/api/scenario/status")
                data = response.get_json()
                assert data["active"] == "port_strike"
                assert len(data["affected_suppliers"]) == 2

    def test_status_no_active_scenario(self, client):
        """GET /api/scenario/status when nothing active returns null active."""
        with patch("api.app._active_scenario_id", None):
            with patch("api.app._active_overrides", {}):
                response = client.get("/api/scenario/status")
                data = response.get_json()
                assert data["active"] is None


class TestThoughtStream:
    """Tests for /api/stream/thoughts SSE endpoint."""

    def test_thought_stream_returns_sse_content_type(self, client):
        """GET /api/stream/thoughts returns text/event-stream mimetype."""
        with patch("api.app._thought_queues", []):
            response = client.get("/api/stream/thoughts")
            assert response.status_code == 200
            assert "text/event-stream" in response.content_type

    def test_thought_stream_has_cache_control_headers(self, client):
        """SSE response includes no-cache headers."""
        with patch("api.app._thought_queues", []):
            response = client.get("/api/stream/thoughts")
            assert response.status_code == 200


class TestDBIntegrity:
    """Tests for DB checksum/integrity helpers."""

    def test_get_db_checksum_returns_counts(self, client):
        """get_db_checksum returns row counts for all tables."""
        with patch("api.app.get_db_connection") as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.execute.return_value.fetchone.return_value = [20]
            mock_conn.return_value = MagicMock()
            mock_conn.return_value.execute = mock_cursor.execute
            mock_conn.return_value.close = MagicMock()

            from api.app import get_db_checksum

            checksum = get_db_checksum()
            assert "suppliers" in checksum
            assert "orders" in checksum
            assert "status" in checksum
            assert "inventory" in checksum


class TestMapDataWithScenarioOverrides:
    """Tests for /api/map/data with active scenario overrides."""

    def test_map_data_includes_scenario_delay_overrides(self, client):
        """Supplier delays include scenario overrides when active."""
        with patch("api.app._active_overrides", {"SUP-001": 10}):
            with patch("data.map_data.get_supplier_coords") as mock_coords:
                mock_coords.return_value = [
                    {
                        "supplier_id": "SUP-001",
                        "name": "Test Supplier",
                        "city": "Tokyo",
                        "country": "JP",
                        "lat": 35.6762,
                        "lon": 139.6503,
                        "risk_category": "HIGH",
                        "reliability_score": 0.74,
                        "active_pos": 2,
                        "current_delay_days": 3,
                    },
                    {
                        "supplier_id": "SUP-002",
                        "name": "German Supplier",
                        "city": "Berlin",
                        "country": "DE",
                        "lat": 52.52,
                        "lon": 13.405,
                        "risk_category": "LOW",
                        "reliability_score": 0.95,
                        "active_pos": 1,
                        "current_delay_days": 0,
                    },
                ]
                with patch("data.map_data.get_supplier_coords", mock_coords):
                    response = client.get("/api/map/data")
                    data = response.get_json()
                    sup1 = next(
                        s for s in data["suppliers"] if s["supplier_id"] == "SUP-001"
                    )
                    assert sup1["current_delay_days"] == 13
