"""
agent/tools.py — R_agent Tools (The "Hands")

==============================================================
WHAT THESE TOOLS DO (Read this carefully!)
==============================================================
These are Python functions that R_agent is allowed to call.
They connect the AI brain (Gemini) to our data sources:
  1. SQLite (Structured facts: orders, stock, prices)
  2. ChromaDB (Semantic context: news, global events)

Each function is designed to be called by an LLM. The docstrings
tell the LLM exactly when and how to use them.
==============================================================
"""

import os
import sqlite3
import pandas as pd
import chromadb
from datetime import datetime
import sys
from typing import Optional, List, Any

# ── Import central config ─────────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# ── Helper: SQL Connection ────────────────────────────────────────────────────
def get_db_connection():
    """Returns a connection to our SQLite database."""
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


# ── Helper: Vector DB Client ──────────────────────────────────────────────────
def get_vector_client():
    """Returns the ChromaDB client."""
    return chromadb.PersistentClient(path=config.VECTOR_STORE_DIR)


# ==============================================================================
# TOOL 1: get_delayed_orders
# ==============================================================================
def get_delayed_orders(
    min_delay_days: int = 1, criticality: Optional[str] = None
) -> str:
    """
    Search for purchase orders that are currently delayed.
    Use this at the beginning of any risk check.

    Args:
        min_delay_days: Minimum days late (default 1)
        criticality: 'HIGH', 'MEDIUM', or 'LOW' (optional)
    """
    query = """
    SELECT po.*, ss.delay_days, ss.delay_reason, ss.confirmed_delivery
    FROM purchase_orders po
    JOIN supplier_status ss ON po.po_id = ss.po_id
    WHERE ss.delay_days >= ?
    """
    params: List[Any] = [min_delay_days]

    if criticality:
        query += " AND po.criticality = ?"
        params.append(criticality)

    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        return "No delayed orders found matching these criteria."
    return df.to_markdown(index=False)


# ==============================================================================
# TOOL 2: get_inventory_status
# ==============================================================================
def get_inventory_status(part_number: str) -> str:
    """
    Check the warehouse stock and days-of-cover for a specific part.
    Use this to see if a delay will actually stop the production line.
    """
    query = "SELECT * FROM inventory WHERE part_number = ?"
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=[part_number])
    conn.close()

    if df.empty:
        return f"No inventory data found for part {part_number}."
    return df.to_markdown(index=False)


# ==============================================================================
# TOOL 3: get_supplier_info
# ==============================================================================
def get_supplier_info(supplier_id: str) -> str:
    """
    Get detailed profile of a supplier including reliability and alternative backup.
    """
    query = "SELECT * FROM suppliers WHERE supplier_id = ?"
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=[supplier_id])
    conn.close()

    if df.empty:
        return f"Supplier {supplier_id} not found."
    return df.to_markdown(index=False)


# ==============================================================================
# TOOL 4: search_global_events
# ==============================================================================
def search_global_events(query: str, n_results: int = 3) -> str:
    """
    Semantically search for external news/disruptions (port strikes, weather, etc.)
    that might be linked to a delay.
    """
    client = get_vector_client()
    collection = client.get_collection("global_events")

    results = collection.query(query_texts=[query], n_results=n_results)

    documents = results.get("documents") or [[]]
    metadatas = results.get("metadatas") or [[]]

    if not documents[0]:
        return "No relevant global events found."

    output = "## RELEVANT GLOBAL EVENTS\n\n"
    for i in range(len(documents[0])):
        doc = documents[0][i]
        meta = metadatas[0][i] if metadatas[0] else {}
        output += f"### EVENT {i + 1}: {meta.get('event_type', 'Unknown')} at {meta.get('location', 'Unknown')}\n"
        output += f"- **Date:** {meta.get('event_date', 'Unknown')}\n"
        output += f"- **Severity:** {meta.get('severity', 'Unknown')}\n"
        output += f"- **Impact:** {meta.get('estimated_delay_days', 'N/A')} days estimated delay\n"
        output += f"- **Description:** {doc}\n\n"

    return output


# ==============================================================================
# TOOL 5: calculate_risk_score
# ==============================================================================
def calculate_risk_score(po_id: str) -> str:
    """
    Calculates a single 'Resilience Score' (0-100) for an order.
    Higher score = higher danger to production.
    """
    query = """
    SELECT po.criticality, ss.delay_days, inv.days_of_cover, sup.reliability_score
    FROM purchase_orders po
    JOIN supplier_status ss ON po.po_id = ss.po_id
    JOIN inventory inv ON po.part_number = inv.part_number
    JOIN suppliers sup ON po.supplier_id = sup.supplier_id
    WHERE po.po_id = ?
    """
    conn = get_db_connection()
    row = conn.execute(query, [po_id]).fetchone()
    conn.close()

    if not row:
        return f"Order {po_id} not found in database."

    # 🧮 LOGIC:
    score = 0
    factors = []

    # 1. Delay vs Stock (The most critical factor)
    if row["delay_days"] >= row["days_of_cover"]:
        score += 50
        factors.append(
            f"CRITICAL: Delay ({row['delay_days']}d) ≥ Stock Cover ({row['days_of_cover']}d)"
        )
    elif row["delay_days"] > 0:
        score += 20
        factors.append(
            f"WARNING: Delay ({row['delay_days']}d) consumes inventory buffer"
        )

    # 2. Criticality
    if row["criticality"] == "HIGH":
        score += 25
        factors.append("HIGH: Part is critical for production line")
    elif row["criticality"] == "MEDIUM":
        score += 10

    # 3. Supplier Unreliability
    if row["reliability_score"] < 0.85:
        score += 15
        factors.append(
            f"LOW RELIABILITY: Supplier historical score is {row['reliability_score']}"
        )

    # Final Classification
    level = "LOW"
    if score >= config.RISK_CRITICAL_THRESHOLD:
        level = "🚨 CRITICAL"
    elif score >= config.RISK_HIGH_THRESHOLD:
        level = "⚠️ HIGH"
    elif score >= config.RISK_MEDIUM_THRESHOLD:
        level = "🟡 MEDIUM"

    return f"""
# RISK ASSESSMENT FOR {po_id}
- **SCORE:** {score} / 100
- **LEVEL:** {level}
- **FACTORS:**
  - {chr(10).join(factors) if factors else "No significant risk factors detected."}
"""


# ==============================================================================
# TOOL 6: get_alternative_supplier
# ==============================================================================
def get_alternative_supplier(part_number: str) -> str:
    """
    Find backup suppliers for a part. Call this when an order is at CRITICAL risk.
    """
    # In our demo, suppliers.csv has a manual backup. Let's find it.
    query = """
    SELECT sup_alt.* 
    FROM suppliers sup_orig
    JOIN suppliers sup_alt ON sup_orig.alternative_supplier_id = sup_alt.supplier_id
    JOIN purchase_orders po ON po.supplier_id = sup_orig.supplier_id
    WHERE po.part_number = ?
    LIMIT 1
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=[part_number])
    conn.close()

    if df.empty:
        return f"No documented alternative supplier found for part {part_number}."
    return "## SUGGESTED PLAN B (Alternative Supplier)\n\n" + df.to_markdown(
        index=False
    )


# ==============================================================================
# TOOL 7: send_risk_alert
# ==============================================================================
def send_risk_alert(
    po_id: str, risk_score: int, detailed_summary: str, mitigation_plan: str
) -> str:
    """
    Formally alerts the procurement manager about a supply chain risk.
    It generates a high-quality PDF report and sends it via email.

    :param po_id: The ID of the affected order (e.g., PO-2024-001).
    :param risk_score: The calculated 0-100 score.
    :param detailed_summary: A 2-3 sentence explanation of the cause.
    :param mitigation_plan: The suggested fix (e.g., alternative supplier).
    """
    from alerts.pdf_generator import generate_risk_report
    from alerts.notifier import Notifier

    # 1. Generate the PDF Report
    pdf_path = generate_risk_report(
        po_id, risk_score, detailed_summary, mitigation_plan
    )

    # 2. Trigger the Notifier
    notifier = Notifier()
    subject = f"🚨 RESILIENCE ALERT: {po_id} (Score: {risk_score})"
    message = f"""R_agent has detected a supply chain disruption.
    
---
Order: {po_id}
Risk Score: {risk_score} / 100
---

{detailed_summary}

Please review the attached PDF for the full mitigation plan and alternative supplier details.
"""
    status = notifier.send_risk_alert(subject, message, pdf_path=pdf_path)

    return f"✅ Alert system triggered for {po_id}. PDF Report: {pdf_path}. Status: {status}"
