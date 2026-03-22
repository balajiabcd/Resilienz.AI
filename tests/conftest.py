"""
tests/conftest.py — Shared pytest fixtures
"""

import os
import sys
import pytest
import tempfile
import sqlite3
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging_config import test_logger, log_with_context, get_test_run_id

_test_run_id = None


def pytest_configure(config):
    global _test_run_id
    _test_run_id = get_test_run_id()
    log_with_context(
        test_logger,
        "INFO",
        f"=== TEST RUN STARTED ===",
        run_id=_test_run_id,
        pytest_args=str(config.args),
    )


def pytest_sessionfinish(session, exitstatus):
    status_map = {0: "PASSED", 1: "FAILED", 2: "ERROR", 3: "INTERRUPTED"}
    status = status_map.get(exitstatus, f"UNKNOWN ({exitstatus})")
    log_with_context(
        test_logger,
        "INFO",
        f"=== TEST RUN COMPLETED ===",
        run_id=_test_run_id,
        status=status,
        exit_code=exitstatus,
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        if report.passed:
            log_with_context(
                test_logger,
                "INFO",
                f"TEST PASSED",
                test=item.nodeid,
                duration=f"{report.duration:.3f}s",
            )
        elif report.failed:
            log_with_context(
                test_logger,
                "ERROR",
                f"TEST FAILED",
                test=item.nodeid,
                duration=f"{report.duration:.3f}s",
                error=str(report.longrepr)[:200] if report.longrepr else "No details",
            )
    elif report.when == "setup" and report.failed:
        log_with_context(
            test_logger,
            "ERROR",
            f"TEST SETUP FAILED",
            test=item.nodeid,
        )
    elif report.when == "teardown" and report.failed:
        log_with_context(
            test_logger,
            "ERROR",
            f"TEST TEARDOWN FAILED",
            test=item.nodeid,
        )


@pytest.fixture
def mock_config(monkeypatch):
    """Mock config with test-safe values."""
    test_dir = tempfile.mkdtemp()
    db_path = os.path.join(test_dir, "test_resilienz.db")
    vector_dir = os.path.join(test_dir, "vector_store")
    os.makedirs(vector_dir, exist_ok=True)

    monkeypatch.setattr("config.BASE_DIR", test_dir)
    monkeypatch.setattr("config.DATA_DIR", test_dir)
    monkeypatch.setattr("config.VECTOR_STORE_DIR", vector_dir)
    monkeypatch.setattr("config.SQLITE_DB_PATH", db_path)
    monkeypatch.setattr("config.OPENROUTER_API_KEY", "test-api-key")
    monkeypatch.setattr("config.SMTP_PASSWORD", "")
    monkeypatch.setattr("config.RISK_CRITICAL_THRESHOLD", 70)
    monkeypatch.setattr("config.RISK_HIGH_THRESHOLD", 45)
    monkeypatch.setattr("config.RISK_MEDIUM_THRESHOLD", 20)
    monkeypatch.setattr("config.DATA_SEED", 42)
    monkeypatch.setattr("config.NUM_SUPPLIERS", 20)
    monkeypatch.setattr("config.NUM_PURCHASE_ORDERS", 50)
    return {
        "test_dir": test_dir,
        "db_path": db_path,
        "vector_dir": vector_dir,
    }


@pytest.fixture
def temp_db(mock_config):
    """Create a temporary SQLite database with sample data."""
    conn = sqlite3.connect(mock_config["db_path"])
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE suppliers (
            supplier_id TEXT PRIMARY KEY,
            supplier_name TEXT,
            country TEXT,
            city TEXT,
            reliability_score REAL,
            avg_delay_days REAL,
            risk_category TEXT,
            alternative_supplier_id TEXT,
            contact_email TEXT,
            payment_terms_days INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE purchase_orders (
            po_id TEXT PRIMARY KEY,
            supplier_id TEXT,
            supplier_name TEXT,
            part_number TEXT,
            part_description TEXT,
            quantity_ordered INTEGER,
            unit_price_eur REAL,
            order_date TEXT,
            expected_delivery TEXT,
            destination_line TEXT,
            criticality TEXT,
            status TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE supplier_status (
            po_id TEXT PRIMARY KEY,
            supplier_id TEXT,
            last_update TEXT,
            confirmed_delivery TEXT,
            delay_days INTEGER,
            delay_reason TEXT,
            confidence_level TEXT,
            tracking_number TEXT,
            current_location TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE inventory (
            part_number TEXT PRIMARY KEY,
            part_description TEXT,
            stock_quantity INTEGER,
            min_stock_level INTEGER,
            days_of_cover REAL,
            daily_consumption REAL,
            warehouse_location TEXT
        )
    """)

    conn.execute(
        "INSERT INTO suppliers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            "SUP-001",
            "Test Supplier GmbH",
            "DE",
            "Berlin",
            0.95,
            0.5,
            "LOW",
            "SUP-002",
            "orders@test.de",
            30,
        ],
    )
    conn.execute(
        "INSERT INTO suppliers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            "SUP-002",
            "Backup Supplier AG",
            "DE",
            "Munich",
            0.75,
            2.0,
            "MEDIUM",
            "SUP-001",
            "orders@backup.de",
            45,
        ],
    )

    conn.execute(
        "INSERT INTO purchase_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            "PO-2024-001",
            "SUP-001",
            "Test Supplier GmbH",
            "AX-7741-B",
            "Hydraulic valve",
            100,
            50.0,
            "2024-01-01",
            "2024-02-01",
            "LINE-A1",
            "HIGH",
            "OPEN",
        ],
    )
    conn.execute(
        "INSERT INTO purchase_orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            "PO-2024-002",
            "SUP-002",
            "Backup Supplier AG",
            "SN-9981-C",
            "Proximity sensor",
            200,
            25.0,
            "2024-01-15",
            "2024-03-01",
            "LINE-B1",
            "MEDIUM",
            "OPEN",
        ],
    )

    conn.execute(
        "INSERT INTO supplier_status VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            "PO-2024-001",
            "SUP-001",
            "2024-01-20",
            "2024-02-09",
            8,
            "Port strike Hamburg",
            "LOW",
            "DHL-1234567",
            "Hamburg Port",
        ],
    )
    conn.execute(
        "INSERT INTO supplier_status VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            "PO-2024-002",
            "SUP-002",
            "2024-01-25",
            "2024-03-01",
            0,
            "",
            "HIGH",
            "DHL-7654321",
            "Delivered",
        ],
    )

    conn.execute(
        "INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?, ?)",
        ["AX-7741-B", "Hydraulic valve 12mm", 30, 36, 2.5, 12.0, "RACK-A-5"],
    )
    conn.execute(
        "INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?, ?)",
        ["SN-9981-C", "Proximity sensor NPN 24V", 200, 50, 10.0, 20.0, "RACK-B-3"],
    )

    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def mock_chroma_collection():
    """Mock ChromaDB collection for vector search tests."""
    mock = MagicMock()
    mock.query.return_value = {
        "documents": [
            ["Hamburg port strike causing major delays for container shipments"]
        ],
        "metadatas": [
            [
                {
                    "event_id": "EVT-001",
                    "event_type": "PORT_STRIKE",
                    "location": "Hamburg, Germany",
                    "event_date": "2024-01-15",
                    "severity": "HIGH",
                    "estimated_delay_days": 7,
                }
            ]
        ],
        "ids": [["EVT-001"]],
        "distances": [[0.1]],
    }
    return mock


@pytest.fixture
def mock_requests_post():
    """Mock requests.post for API testing."""
    with patch("requests.post") as mock:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"role": "assistant", "content": "Test response from LLM"}}
            ]
        }
        mock.return_value = mock_response
        yield mock


@pytest.fixture
def sample_tools():
    """Sample tool functions for testing."""

    def dummy_tool_1(arg1: str) -> str:
        """First dummy tool for testing."""
        return f"Result for {arg1}"

    def dummy_tool_2(arg1: str, arg2: int = 10) -> str:
        """Second dummy tool with default argument."""
        return f"Result: {arg1} with {arg2}"

    return [dummy_tool_1, dummy_tool_2]
