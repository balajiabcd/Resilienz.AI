"""
tests/data/test_generate_data.py — Tests for data/generate_data.py

Tests data generation functions for suppliers, orders, inventory, and events.
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
import tempfile
import os

import sys
import os as os_module

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import config
import data.generate_data as gd
from data.generate_data import (
    generate_suppliers,
    generate_purchase_orders,
    generate_supplier_status,
    generate_inventory,
    generate_global_events,
    load_into_sqlite,
    load_into_vector_db,
)


class TestGenerateSuppliers:
    """Tests for generate_suppliers function."""

    def test_returns_dataframe(self):
        result = generate_suppliers()
        assert isinstance(result, pd.DataFrame)

    def test_creates_correct_count(self):
        result = generate_suppliers()
        assert len(result) == config.NUM_SUPPLIERS

    def test_has_required_columns(self):
        result = generate_suppliers()
        required_cols = [
            "supplier_id",
            "supplier_name",
            "reliability_score",
            "alternative_supplier_id",
            "risk_category",
        ]
        for col in required_cols:
            assert col in result.columns

    def test_saves_csv_file(self):
        tmpdir = tempfile.mkdtemp()
        original_dir = config.DATA_DIR
        try:
            config.DATA_DIR = tmpdir
            gd.DATA_DIR = tmpdir
            generate_suppliers()
            csv_path = os.path.join(tmpdir, "suppliers.csv")
            assert os.path.exists(csv_path)
        finally:
            config.DATA_DIR = original_dir
            gd.DATA_DIR = original_dir

    def test_reliability_scores_valid_range(self):
        result = generate_suppliers()
        assert result["reliability_score"].min() >= 0
        assert result["reliability_score"].max() <= 1

    def test_has_alternative_suppliers(self):
        result = generate_suppliers()
        assert not result["alternative_supplier_id"].isna().all()


class TestGeneratePurchaseOrders:
    """Tests for generate_purchase_orders function."""

    def test_returns_dataframe(self):
        suppliers_df = pd.DataFrame(
            {
                "supplier_id": ["SUP-001", "SUP-002"],
                "supplier_name": ["Supplier A", "Supplier B"],
                "reliability_score": [0.9, 0.8],
                "avg_delay_days": [1.0, 2.0],
                "risk_category": ["LOW", "MEDIUM"],
                "alternative_supplier_id": ["SUP-002", "SUP-001"],
                "contact_email": ["a@test.de", "b@test.de"],
                "payment_terms_days": [30, 45],
                "country": ["DE", "DE"],
                "city": ["Berlin", "Munich"],
            }
        )
        result = generate_purchase_orders(suppliers_df)
        assert isinstance(result, pd.DataFrame)

    def test_creates_correct_count(self):
        suppliers_df = pd.DataFrame(
            {
                "supplier_id": ["SUP-001"],
                "supplier_name": ["Test"],
                "reliability_score": [0.9],
                "avg_delay_days": [1.0],
                "risk_category": ["LOW"],
                "alternative_supplier_id": ["SUP-001"],
                "contact_email": ["test@test.de"],
                "payment_terms_days": [30],
                "country": ["DE"],
                "city": ["Berlin"],
            }
        )
        result = generate_purchase_orders(suppliers_df)
        assert len(result) == config.NUM_PURCHASE_ORDERS

    def test_first_order_uses_first_part_catalog(self):
        suppliers_df = pd.DataFrame(
            {
                "supplier_id": ["SUP-001"],
                "supplier_name": ["Test"],
                "reliability_score": [0.9],
                "avg_delay_days": [1.0],
                "risk_category": ["LOW"],
                "alternative_supplier_id": ["SUP-001"],
                "contact_email": ["test@test.de"],
                "payment_terms_days": [30],
                "country": ["DE"],
                "city": ["Berlin"],
            }
        )
        result = generate_purchase_orders(suppliers_df)
        assert result.iloc[0]["part_number"] == "AX-7741-B"
        assert result.iloc[0]["criticality"] == "HIGH"


class TestGenerateSupplierStatus:
    """Tests for generate_supplier_status function."""

    def test_returns_dataframe(self):
        orders_df = pd.DataFrame(
            {
                "po_id": ["PO-001", "PO-002"],
                "supplier_id": ["SUP-001", "SUP-002"],
                "expected_delivery": ["2024-02-01", "2024-02-15"],
                "part_number": ["PART-1", "PART-2"],
                "part_description": ["Desc 1", "Desc 2"],
                "quantity_ordered": [100, 200],
                "unit_price_eur": [10.0, 20.0],
                "order_date": ["2024-01-01", "2024-01-15"],
                "destination_line": ["LINE-A1", "LINE-B1"],
                "criticality": ["HIGH", "LOW"],
                "status": ["OPEN", "OPEN"],
                "supplier_name": ["S1", "S2"],
            }
        )
        suppliers_df = pd.DataFrame(
            {
                "supplier_id": ["SUP-001", "SUP-002"],
                "supplier_name": ["S1", "S2"],
                "reliability_score": [0.9, 0.8],
                "risk_category": ["LOW", "MEDIUM"],
            }
        )
        result = generate_supplier_status(orders_df, suppliers_df)
        assert isinstance(result, pd.DataFrame)

    def test_first_order_is_delayed(self):
        orders_df = pd.DataFrame(
            {
                "po_id": ["PO-2024-001", "PO-2024-002"],
                "supplier_id": ["SUP-001", "SUP-002"],
                "expected_delivery": ["2024-02-01", "2024-02-15"],
                "part_number": ["PART-1", "PART-2"],
                "part_description": ["Desc 1", "Desc 2"],
                "quantity_ordered": [100, 200],
                "unit_price_eur": [10.0, 20.0],
                "order_date": ["2024-01-01", "2024-01-15"],
                "destination_line": ["LINE-A1", "LINE-B1"],
                "criticality": ["HIGH", "LOW"],
                "status": ["OPEN", "OPEN"],
                "supplier_name": ["S1", "S2"],
            }
        )
        suppliers_df = pd.DataFrame(
            {
                "supplier_id": ["SUP-001", "SUP-002"],
                "supplier_name": ["S1", "S2"],
                "reliability_score": [0.9, 0.8],
                "risk_category": ["LOW", "MEDIUM"],
            }
        )
        result = generate_supplier_status(orders_df, suppliers_df)
        assert result.iloc[0]["delay_days"] == 8


class TestGenerateInventory:
    """Tests for generate_inventory function."""

    def test_returns_dataframe(self):
        orders_df = pd.DataFrame(
            {
                "part_number": ["PART-001", "PART-002"],
                "part_description": ["Part A", "Part B"],
            }
        )
        result = generate_inventory(orders_df)
        assert isinstance(result, pd.DataFrame)

    def test_ax_part_has_low_stock(self):
        orders_df = pd.DataFrame(
            {
                "part_number": ["AX-7741-B", "PART-002"],
                "part_description": ["Hydraulic valve", "Other part"],
            }
        )
        result = generate_inventory(orders_df)
        ax_row = result[result["part_number"] == "AX-7741-B"].iloc[0]
        assert ax_row["days_of_cover"] == 2.5


class TestGenerateGlobalEvents:
    """Tests for generate_global_events function."""

    def test_returns_dataframe(self):
        result = generate_global_events()
        assert isinstance(result, pd.DataFrame)

    def test_has_required_columns(self):
        result = generate_global_events()
        required_cols = [
            "event_id",
            "event_type",
            "location",
            "severity",
            "description",
        ]
        for col in required_cols:
            assert col in result.columns

    def test_contains_hamburg_port_event(self):
        result = generate_global_events()
        locations = result["location"].astype(str).tolist()
        event_types = result["event_type"].astype(str).tolist()
        assert any("Hamburg" in str(loc) for loc in locations)
        assert any("PORT_STRIKE" in str(et) for et in event_types)


class TestLoadIntoSqlite:
    """Tests for load_into_sqlite function."""

    def test_creates_tables(self):
        tmpdir = tempfile.mkdtemp()
        original_path = config.SQLITE_DB_PATH
        try:
            config.SQLITE_DB_PATH = os.path.join(tmpdir, "test.db")
            gd.SQLITE_DB_PATH = config.SQLITE_DB_PATH

            suppliers_df = pd.DataFrame(
                {"supplier_id": ["S1"], "supplier_name": ["Test"]}
            )
            orders_df = pd.DataFrame({"po_id": ["PO1"], "supplier_id": ["S1"]})
            status_df = pd.DataFrame({"po_id": ["PO1"], "delay_days": [0]})
            inventory_df = pd.DataFrame({"part_number": ["P1"], "stock": [100]})

            load_into_sqlite(suppliers_df, orders_df, status_df, inventory_df)
            assert os.path.exists(config.SQLITE_DB_PATH)
        finally:
            config.SQLITE_DB_PATH = original_path
            gd.SQLITE_DB_PATH = original_path


class TestLoadIntoVectorDB:
    """Tests for load_into_vector_db function."""

    def test_handles_missing_chromadb(self):
        with patch.dict("sys.modules", {"chromadb": None}):
            events_df = pd.DataFrame(
                {
                    "event_id": ["E1"],
                    "description": ["Test event"],
                    "event_date": ["2024-01-01"],
                    "event_type": ["TEST"],
                    "location": ["Test"],
                    "severity": ["LOW"],
                    "estimated_delay_days": [1],
                    "source": ["Test"],
                    "resolved": [False],
                    "affected_countries": ["DE"],
                }
            )
            load_into_vector_db(events_df)


class TestDataGenerationEdgeCases:
    """Edge case tests for data generation."""

    def test_zero_orders(self):
        suppliers_df = pd.DataFrame(
            {
                "supplier_id": ["SUP-001"],
                "supplier_name": ["Test"],
                "reliability_score": [0.9],
                "avg_delay_days": [1.0],
                "risk_category": ["LOW"],
                "alternative_supplier_id": ["SUP-001"],
                "contact_email": ["test@test.de"],
                "payment_terms_days": [30],
                "country": ["DE"],
                "city": ["Berlin"],
            }
        )
        original_orders = config.NUM_PURCHASE_ORDERS
        try:
            config.NUM_PURCHASE_ORDERS = 0
            gd.NUM_PURCHASE_ORDERS = 0
            result = generate_purchase_orders(suppliers_df)
            assert len(result) == 0
        finally:
            config.NUM_PURCHASE_ORDERS = original_orders
            gd.NUM_PURCHASE_ORDERS = original_orders


class TestDataGenerationStress:
    """Stress tests for data generation."""

    def test_large_order_count(self):
        suppliers_df = pd.DataFrame(
            {
                "supplier_id": [f"SUP-{i:03d}" for i in range(10)],
                "supplier_name": [f"Supplier {i}" for i in range(10)],
                "reliability_score": [0.9] * 10,
                "avg_delay_days": [1.0] * 10,
                "risk_category": ["LOW"] * 10,
                "alternative_supplier_id": [f"SUP-{i:03d}" for i in range(10)],
                "contact_email": [f"s{i}@test.de" for i in range(10)],
                "payment_terms_days": [30] * 10,
                "country": ["DE"] * 10,
                "city": ["Berlin"] * 10,
            }
        )
        original_count = config.NUM_PURCHASE_ORDERS
        try:
            config.NUM_PURCHASE_ORDERS = 50
            gd.NUM_PURCHASE_ORDERS = 50
            result = generate_purchase_orders(suppliers_df)
            assert len(result) == 50
        finally:
            config.NUM_PURCHASE_ORDERS = original_count
            gd.NUM_PURCHASE_ORDERS = original_count
