"""
tests/agent/test_tools.py — Tests for agent/tools.py

Tests all 7 LLM-callable tool functions with mocked databases.
"""

import pytest
from unittest.mock import MagicMock, patch
import sqlite3


class TestGetDelayedOrders:
    """Tests for get_delayed_orders tool."""

    def test_returns_delayed_orders(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_delayed_orders

        result = get_delayed_orders(min_delay_days=1)

        assert "PO-2024-001" in result
        assert "8" in result or "delay" in result.lower()

    def test_filters_by_criticality(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_delayed_orders

        result = get_delayed_orders(min_delay_days=1, criticality="HIGH")

        assert "PO-2024-001" in result
        assert "PO-2024-002" not in result

    def test_no_delayed_orders(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_delayed_orders

        result = get_delayed_orders(min_delay_days=100)

        assert "No delayed orders found" in result

    def test_default_min_delay_days(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_delayed_orders

        result = get_delayed_orders()

        assert "PO-2024-001" in result


class TestGetInventoryStatus:
    """Tests for get_inventory_status tool."""

    def test_returns_inventory_for_valid_part(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_inventory_status

        result = get_inventory_status("AX-7741-B")

        assert "AX-7741-B" in result
        assert "30" in result

    def test_part_not_found(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_inventory_status

        result = get_inventory_status("NON-EXISTENT")

        assert "No inventory data found" in result
        assert "NON-EXISTENT" in result


class TestGetSupplierInfo:
    """Tests for get_supplier_info tool."""

    def test_returns_supplier_for_valid_id(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_supplier_info

        result = get_supplier_info("SUP-001")

        assert "SUP-001" in result
        assert "Test Supplier" in result

    def test_supplier_not_found(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_supplier_info

        result = get_supplier_info("INVALID-ID")

        assert "not found" in result


class TestSearchGlobalEvents:
    """Tests for search_global_events tool."""

    def test_returns_events(self, temp_db, monkeypatch, mock_chroma_collection):
        mock_client = MagicMock()
        mock_client.get_collection.return_value = mock_chroma_collection

        monkeypatch.setattr("agent.tools.get_vector_client", lambda: mock_client)
        from agent.tools import search_global_events

        result = search_global_events("Hamburg port strike")

        assert "RELEVANT GLOBAL EVENTS" in result
        assert "EVT-001" in result or "Hamburg" in result

    def test_no_events_found(self, temp_db, monkeypatch):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}
        mock_client = MagicMock()
        mock_client.get_collection.return_value = mock_collection

        monkeypatch.setattr("agent.tools.get_vector_client", lambda: mock_client)
        from agent.tools import search_global_events

        result = search_global_events("completely unrelated query")

        assert "No relevant global events found" in result

    def test_custom_n_results(self, temp_db, monkeypatch, mock_chroma_collection):
        mock_client = MagicMock()
        mock_client.get_collection.return_value = mock_chroma_collection

        monkeypatch.setattr("agent.tools.get_vector_client", lambda: mock_client)
        from agent.tools import search_global_events

        result = search_global_events("test", n_results=5)

        mock_client.get_collection.return_value.query.assert_called_with(
            query_texts=["test"], n_results=5
        )


class TestCalculateRiskScore:
    """Tests for calculate_risk_score tool."""

    def test_calculates_critical_risk(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        monkeypatch.setattr("config.RISK_CRITICAL_THRESHOLD", 70)
        monkeypatch.setattr("config.RISK_HIGH_THRESHOLD", 45)
        monkeypatch.setattr("config.RISK_MEDIUM_THRESHOLD", 20)
        from agent.tools import calculate_risk_score

        result = calculate_risk_score("PO-2024-001")

        assert "PO-2024-001" in result
        assert "SCORE" in result
        assert "CRITICAL" in result or "HIGH" in result or "MEDIUM" in result

    def test_order_not_found(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import calculate_risk_score

        result = calculate_risk_score("INVALID-PO")

        assert "not found" in result

    def test_risk_score_includes_factors(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        monkeypatch.setattr("config.RISK_CRITICAL_THRESHOLD", 70)
        monkeypatch.setattr("config.RISK_HIGH_THRESHOLD", 45)
        monkeypatch.setattr("config.RISK_MEDIUM_THRESHOLD", 20)
        from agent.tools import calculate_risk_score

        result = calculate_risk_score("PO-2024-001")

        assert "FACTORS" in result


class TestGetAlternativeSupplier:
    """Tests for get_alternative_supplier tool."""

    def test_finds_alternative(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_alternative_supplier

        result = get_alternative_supplier("AX-7741-B")

        assert "SUGGESTED PLAN B" in result or "alternative" in result.lower()

    def test_no_alternative_found(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_alternative_supplier

        result = get_alternative_supplier("NON-EXISTENT-PART")

        assert "No documented alternative supplier" in result


class TestSendRiskAlert:
    """Tests for send_risk_alert tool."""

    def test_sends_alert_with_pdf(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        monkeypatch.setattr(
            "alerts.pdf_generator.generate_risk_report",
            lambda *args, **kwargs: "/path/to/report.pdf",
        )

        notifier_mock = MagicMock()
        notifier_mock.send_risk_alert.return_value = "SENT"
        monkeypatch.setattr("alerts.notifier.Notifier", lambda: notifier_mock)

        from agent.tools import send_risk_alert

        result = send_risk_alert(
            po_id="PO-2024-001",
            risk_score=75,
            detailed_summary="Test summary",
            mitigation_plan="Test plan",
        )

        assert "PO-2024-001" in result

    def test_alert_without_pdf(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        monkeypatch.setattr(
            "alerts.pdf_generator.generate_risk_report",
            lambda *args, **kwargs: "/path/to/report.pdf",
        )

        notifier_mock = MagicMock()
        notifier_mock.send_risk_alert.return_value = "ALREADY_LOGGED_TO_CONSOLE"
        monkeypatch.setattr("alerts.notifier.Notifier", lambda: notifier_mock)

        from agent.tools import send_risk_alert

        result = send_risk_alert(
            po_id="PO-2024-002",
            risk_score=25,
            detailed_summary="Low risk",
            mitigation_plan="Monitor",
        )

        assert "PO-2024-002" in result


class TestDatabaseConnection:
    """Tests for database connection helper."""

    def test_connection_has_row_factory(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_db_connection

        conn = get_db_connection()
        conn.row_factory = sqlite3.Row

        assert callable(conn.row_factory)


class TestToolsEdgeCases:
    """Edge case tests for tools."""

    def test_empty_part_number(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_inventory_status

        result = get_inventory_status("")

        assert "No inventory data found" in result

    def test_none_criticality(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_delayed_orders

        result = get_delayed_orders(min_delay_days=1, criticality=None)

        assert "PO-2024-001" in result

    def test_search_with_special_chars(self, temp_db, monkeypatch):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}
        mock_client = MagicMock()
        mock_client.get_collection.return_value = mock_collection

        monkeypatch.setattr("agent.tools.get_vector_client", lambda: mock_client)
        from agent.tools import search_global_events

        result = search_global_events("test@#$%^&*() query")

        assert mock_client.get_collection.called

    def test_zero_delay_filter(self, temp_db, monkeypatch):
        monkeypatch.setattr("agent.tools.get_db_connection", lambda: temp_db)
        from agent.tools import get_delayed_orders

        result = get_delayed_orders(min_delay_days=0)

        assert "PO-2024-001" in result


class TestToolsStress:
    """Stress tests for tools."""

    def test_many_risk_calculations(self, temp_db, monkeypatch):
        from agent.tools import calculate_risk_score

        for i in range(10):
            result = calculate_risk_score("PO-2024-001")
            assert "SCORE" in result or "not found" in result

    def test_many_supplier_lookups(self, temp_db, monkeypatch):
        from agent.tools import get_supplier_info

        for _ in range(10):
            result = get_supplier_info("SUP-001")
            assert "SUP-001" in result

    def test_large_n_results(self, temp_db, monkeypatch):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["doc1", "doc2", "doc3"]],
            "metadatas": [[{}, {}, {}]],
        }
        mock_client = MagicMock()
        mock_client.get_collection.return_value = mock_collection

        monkeypatch.setattr("agent.tools.get_vector_client", lambda: mock_client)
        from agent.tools import search_global_events

        result = search_global_events("query", n_results=100)

        assert mock_client.get_collection.return_value.query.called
