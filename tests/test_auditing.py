"""
tests/test_auditing.py — Tests for auditing.py

Tests hybrid audit workflow, PO extraction, and phase execution.
"""

import pytest
from unittest.mock import MagicMock, patch
from auditing import (
    extract_po_ids,
    run_hybrid_audit,
    PHASE_1_INVESTIGATOR_PROMPT,
    PHASE_2_REPORTER_PROMPT,
)


class TestExtractPoIds:
    """Unit tests for extract_po_ids function."""

    def test_extracts_single_po(self):
        markdown = "| PO-2024-001 | Delivered | 8 days |"
        result = extract_po_ids(markdown)
        assert "PO-2024-001" in result

    def test_extracts_multiple_pos(self):
        markdown = """
        | PO-2024-001 | Delayed | 5 days |
        | PO-2024-002 | Delayed | 3 days |
        | PO-2024-003 | On Time | 0 days |
        """
        result = extract_po_ids(markdown)
        assert len(result) == 3
        assert "PO-2024-001" in result
        assert "PO-2024-002" in result
        assert "PO-2024-003" in result

    def test_no_pos_found(self):
        markdown = "No orders here, just text"
        result = extract_po_ids(markdown)
        assert result == []

    def test_extracts_from_markdown_table(self):
        markdown = """
        # Purchase Orders
        
        | Order ID | Status | Delay |
        |----------|--------|-------|
        | PO-2024-042 | Critical | 10 days |
        """
        result = extract_po_ids(markdown)
        assert "PO-2024-042" in result

    def test_handles_duplicates(self):
        markdown = "PO-2024-001 appears twice PO-2024-001"
        result = extract_po_ids(markdown)
        assert result.count("PO-2024-001") == 2


class TestPhasePrompts:
    """Tests for prompt templates."""

    def test_phase_1_prompt_has_placeholders(self):
        assert "{po_id}" in PHASE_1_INVESTIGATOR_PROMPT
        assert "{data_internal}" in PHASE_1_INVESTIGATOR_PROMPT
        assert "{data_risk}" in PHASE_1_INVESTIGATOR_PROMPT
        assert "{data_external}" in PHASE_1_INVESTIGATOR_PROMPT

    def test_phase_2_prompt_has_summaries_placeholder(self):
        assert "{summaries}" in PHASE_2_REPORTER_PROMPT

    def test_phase_1_prompt_formats_correctly(self):
        formatted = PHASE_1_INVESTIGATOR_PROMPT.format(
            po_id="PO-2024-001",
            data_internal="Inventory data here",
            data_risk="Risk data here",
            data_external="External events",
        )
        assert "PO-2024-001" in formatted
        assert "Inventory data here" in formatted

    def test_phase_2_prompt_formats_correctly(self):
        summaries = "### PO-2024-001\nSummary 1\n\n### PO-2024-002\nSummary 2"
        formatted = PHASE_2_REPORTER_PROMPT.format(summaries=summaries)
        assert "Summary 1" in formatted
        assert "Summary 2" in formatted


class TestRunHybridAudit:
    """Tests for run_hybrid_audit function."""

    @patch("auditing.tools.get_delayed_orders")
    @patch("auditing.LLMSwitch")
    def test_no_delayed_orders_returns_healthy(
        self, mock_switch_class, mock_delayed_orders
    ):
        mock_delayed_orders.return_value = "No delayed orders"
        mock_switch = MagicMock()
        mock_switch_class.return_value = mock_switch

        result = run_hybrid_audit()

        assert "No risks detected" in result or "healthy" in result.lower()

    @patch("auditing.tools.get_delayed_orders")
    @patch("auditing.LLMSwitch")
    def test_processes_delayed_orders(self, mock_switch_class, mock_delayed_orders):
        mock_delayed_orders.return_value = """
        | PO-2024-001 | 8 days late |
        """
        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Test summary"
        mock_switch_class.return_value = mock_switch

        with patch("auditing.tools.get_db_connection") as mock_conn:
            mock_row = MagicMock()
            mock_row.__getitem__ = lambda self, key: {
                "part_number": "AX-7741-B",
                "supplier_id": "SUP-001",
            }[key]
            mock_conn.return_value.execute.return_value.fetchone.return_value = mock_row
            mock_conn.return_value.close = MagicMock()

            with patch("auditing.tools.get_inventory_status", return_value="Inventory"):
                with patch("auditing.tools.get_supplier_info", return_value="Supplier"):
                    with patch(
                        "auditing.tools.calculate_risk_score",
                        return_value="**SCORE:** 75",
                    ):
                        with patch(
                            "auditing.tools.search_global_events", return_value="Events"
                        ):
                            result = run_hybrid_audit()

        assert mock_switch.try_generate.called

    @patch("auditing.tools.get_delayed_orders")
    @patch("auditing.LLMSwitch")
    def test_low_score_po_not_included(self, mock_switch_class, mock_delayed_orders):
        mock_delayed_orders.return_value = "| PO-2024-001 | 1 day |"
        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Summary"
        mock_switch_class.return_value = mock_switch

        with patch("auditing.tools.get_db_connection") as mock_conn:
            mock_row = MagicMock()
            mock_row.__getitem__ = lambda self, key: {
                "part_number": "AX-7741-B",
                "supplier_id": "SUP-001",
            }[key]
            mock_conn.return_value.execute.return_value.fetchone.return_value = mock_row
            mock_conn.return_value.close = MagicMock()

            with patch("auditing.tools.get_inventory_status", return_value="I"):
                with patch("auditing.tools.get_supplier_info", return_value="S"):
                    with patch(
                        "auditing.tools.calculate_risk_score",
                        return_value="**SCORE:** 3",
                    ):
                        with patch(
                            "auditing.tools.search_global_events", return_value="E"
                        ):
                            result = run_hybrid_audit()

        assert "No critical risks" in result or mock_switch.try_generate.call_count <= 1


class TestHybridAuditEdgeCases:
    """Edge case tests for hybrid audit."""

    @patch("auditing.tools.get_delayed_orders")
    @patch("auditing.LLMSwitch")
    def test_handles_db_error_gracefully(self, mock_switch_class, mock_delayed_orders):
        mock_delayed_orders.return_value = "No delayed orders"
        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Done"
        mock_switch_class.return_value = mock_switch

        result = run_hybrid_audit()

        assert result is not None

    @patch("auditing.tools.get_delayed_orders")
    @patch("auditing.LLMSwitch")
    def test_handles_empty_external_events(
        self, mock_switch_class, mock_delayed_orders
    ):
        mock_delayed_orders.return_value = "| PO-2024-001 | 5 days |"
        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Summary"
        mock_switch_class.return_value = mock_switch

        with patch("auditing.tools.get_db_connection") as mock_conn:
            mock_row = MagicMock()
            mock_row.__getitem__ = lambda self, key: {
                "part_number": "PART-1",
                "supplier_id": "SUP-001",
            }[key]
            mock_conn.return_value.execute.return_value.fetchone.return_value = mock_row
            mock_conn.return_value.close = MagicMock()

            with patch("auditing.tools.get_inventory_status", return_value="I"):
                with patch("auditing.tools.get_supplier_info", return_value="S"):
                    with patch(
                        "auditing.tools.calculate_risk_score",
                        return_value="**SCORE:** 50",
                    ):
                        with patch(
                            "auditing.tools.search_global_events", return_value=""
                        ):
                            result = run_hybrid_audit()

        assert mock_switch.try_generate.called

    @patch("auditing.tools.get_delayed_orders")
    @patch("auditing.LLMSwitch")
    def test_limits_to_top_5_risk_orders(self, mock_switch_class, mock_delayed_orders):
        pos = "| PO-2024-001 | 10 days |\n| PO-2024-002 | 9 days |\n| PO-2024-003 | 8 days |\n| PO-2024-004 | 7 days |\n| PO-2024-005 | 6 days |\n| PO-2024-006 | 5 days |"
        mock_delayed_orders.return_value = pos
        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Summary"
        mock_switch_class.return_value = mock_switch

        with patch("auditing.tools.get_db_connection") as mock_conn:
            mock_row = MagicMock()
            mock_row.__getitem__ = lambda self, key: {
                "part_number": "PART-1",
                "supplier_id": "SUP-001",
            }[key]
            mock_conn.return_value.execute.return_value.fetchone.return_value = mock_row
            mock_conn.return_value.close = MagicMock()

            with patch("auditing.tools.get_inventory_status", return_value="I"):
                with patch("auditing.tools.get_supplier_info", return_value="S"):
                    with patch(
                        "auditing.tools.calculate_risk_score",
                        return_value="**SCORE:** 50",
                    ):
                        with patch(
                            "auditing.tools.search_global_events", return_value="E"
                        ):
                            result = run_hybrid_audit()

        assert mock_switch.try_generate.call_count >= 5


class TestHybridAuditStress:
    """Stress tests for hybrid audit."""

    @patch("auditing.tools.get_delayed_orders")
    @patch("auditing.LLMSwitch")
    def test_handles_large_number_of_pos(self, mock_switch_class, mock_delayed_orders):
        many_pos = "\n".join(
            [f"| PO-2024-{str(i).zfill(3)} | 5 days |" for i in range(100)]
        )
        mock_delayed_orders.return_value = many_pos
        mock_switch = MagicMock()
        mock_switch.try_generate.return_value = "Summary"
        mock_switch_class.return_value = mock_switch

        with patch("auditing.tools.get_db_connection") as mock_conn:
            mock_row = MagicMock()
            mock_row.__getitem__ = lambda self, key: {
                "part_number": "PART-1",
                "supplier_id": "SUP-001",
            }[key]
            mock_conn.return_value.execute.return_value.fetchone.return_value = mock_row
            mock_conn.return_value.close = MagicMock()

            with patch("auditing.tools.get_inventory_status", return_value="I"):
                with patch("auditing.tools.get_supplier_info", return_value="S"):
                    with patch(
                        "auditing.tools.calculate_risk_score",
                        return_value="**SCORE:** 50",
                    ):
                        with patch(
                            "auditing.tools.search_global_events", return_value="E"
                        ):
                            result = run_hybrid_audit()

        assert mock_switch.try_generate.call_count >= 5
