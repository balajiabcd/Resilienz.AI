"""
api/app.py — Resilienz.AI Backend Server

Connects the AI Agent to the Dashboard UI.
"""

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import os
import sys
import sqlite3
import json
import queue

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from logging_config import app_logger, log_with_context
from agent.brain import RAgent

app = Flask(__name__)
CORS(app)

agent = RAgent()
log_with_context(
    app_logger,
    "INFO",
    "Resilienz.AI API initialized",
    host=config.FLASK_HOST,
    port=config.FLASK_PORT,
)

# ── Scenario System (In-Memory Overrides + ChromaDB) ───────────────────────────
SCENARIOS = {
    "suez_blockage": {
        "name": "Suez Canal Blockage",
        "affected_countries": ["JP", "CN", "KR"],
        "delay_modifier": 10,
        "chroma_event": {
            "event_id": "SCENARIO-SUEZ",
            "event_type": "GEOPOLITICAL",
            "location": "Suez Canal",
            "affected_countries": "GLOBAL",
            "severity": "CRITICAL",
            "estimated_delay_days": 14,
            "description": "Simulated Red Sea crisis — rerouting around Cape of Good Hope adds 10-14 days for Asian suppliers",
            "source": "Simulated Event",
            "resolved": False,
        },
    },
    "port_strike": {
        "name": "Port Strike — Hamburg",
        "affected_countries": ["DE"],
        "delay_modifier": 7,
        "chroma_event": {
            "event_id": "SCENARIO-HAMBURG",
            "event_type": "PORT_STRIKE",
            "location": "Hamburg, Germany",
            "affected_countries": "DE, NL, BE",
            "severity": "HIGH",
            "estimated_delay_days": 7,
            "description": "Simulated dockworkers' strike at Hamburg Port — German supplier delays",
            "source": "Simulated Event",
            "resolved": False,
        },
    },
    "energy_crisis": {
        "name": "Energy Crisis — Germany",
        "affected_countries": ["DE"],
        "delay_modifier": 4,
        "chroma_event": {
            "event_id": "SCENARIO-ENERGY",
            "event_type": "ENERGY_SHORTAGE",
            "location": "Germany (Nationwide)",
            "affected_countries": "DE",
            "severity": "MEDIUM",
            "estimated_delay_days": 4,
            "description": "Simulated energy shortage — German industrial production reduced by 20%",
            "source": "Simulated Event",
            "resolved": False,
        },
    },
}

_active_scenario_id = None
_active_overrides = {}
_injected_chroma_ids = []
_original_chroma_state = None
_saved_chroma_events = []

_thought_queues = []


def emit_thought(step: str, detail: str = ""):
    event = json.dumps({"step": step, "detail": detail})
    for q in _thought_queues[:]:
        try:
            q.put_nowait(event)
        except queue.Full:
            _thought_queues.remove(q)


# ── HELPERS ───────────────────────────────────────────────────────────────────
def get_db_connection():
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── ENDPOINTS ─────────────────────────────────────────────────────────────────


@app.route("/", methods=["GET"])
def home():
    """Welcome page to confirm the engine is running."""
    return """
    <h1>🛡️ Resilienz.AI Engine is LIVE</h1>
    <p>The API is running. To view the dashboard, open <b>dashboard/index.html</b> in your browser.</p>
    <ul>
        <li><b>API Status:</b> Healthy</li>
        <li><b>Primary Model:</b> Gemini</li>
    </ul>
    """


@app.route("/api/dashboard/summary", methods=["GET"])
def get_summary():
    """Returns basic counts for the UI tiles."""
    conn = get_db_connection()
    counts = {
        "suppliers": conn.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0],
        "orders": conn.execute("SELECT COUNT(*) FROM purchase_orders").fetchone()[0],
        "delayed": conn.execute(
            "SELECT COUNT(*) FROM supplier_status WHERE delay_days > 0"
        ).fetchone()[0],
        "inventory": conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0],
    }
    conn.close()
    return jsonify(counts)


@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    """Lists current inventory levels."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM inventory").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/orders/critical", methods=["GET"])
def get_critical_orders():
    """Lists high-criticality orders."""
    conn = get_db_connection()
    query = """
    SELECT po.*, ss.delay_days, ss.delay_reason
    FROM purchase_orders po
    JOIN supplier_status ss ON po.po_id = ss.po_id
    WHERE po.criticality = 'HIGH'
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/suppliers", methods=["GET"])
def get_suppliers():
    """Lists all active suppliers with full details."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM suppliers").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/orders", methods=["GET"])
def get_all_orders():
    """Lists all purchase orders with supplier info."""
    conn = get_db_connection()
    query = """
    SELECT po.*, ss.delay_days, ss.delay_reason, ss.confirmed_delivery,
           ss.confidence_level, ss.tracking_number, ss.current_location
    FROM purchase_orders po
    LEFT JOIN supplier_status ss ON po.po_id = ss.po_id
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/orders/in-transit", methods=["GET"])
def get_in_transit_orders():
    """Lists orders currently in transit (not delivered, no delay)."""
    conn = get_db_connection()
    query = """
    SELECT po.*, ss.delay_days, ss.delay_reason, ss.confirmed_delivery,
           ss.confidence_level, ss.tracking_number, ss.current_location
    FROM purchase_orders po
    LEFT JOIN supplier_status ss ON po.po_id = ss.po_id
    WHERE po.status != 'DELIVERED' AND (ss.delay_days IS NULL OR ss.delay_days = 0)
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/orders/delayed", methods=["GET"])
def get_delayed_orders():
    """Lists all delayed orders with full status details."""
    conn = get_db_connection()
    query = """
    SELECT po.*, ss.delay_days, ss.delay_reason, ss.confirmed_delivery,
           ss.confidence_level, ss.tracking_number, ss.current_location
    FROM purchase_orders po
    JOIN supplier_status ss ON po.po_id = ss.po_id
    WHERE ss.delay_days > 0
    ORDER BY ss.delay_days DESC
    """
    rows = conn.execute(query).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


@app.route("/api/agent/audit", methods=["POST"])
def trigger_audit():
    """Forces the agent to perform its autonomous reasoning loop."""
    log_with_context(app_logger, "INFO", "Risk audit triggered via API")
    try:
        report = agent.run_risk_audit()
        log_with_context(
            app_logger, "INFO", "Risk audit completed", report_length=len(str(report))
        )
        return jsonify({"report": report})
    except Exception as e:
        log_with_context(app_logger, "ERROR", f"Risk audit failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/agent/chat", methods=["POST"])
def agent_chat():
    """Allows individual user questions."""
    data = request.json
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        log_with_context(
            app_logger,
            "INFO",
            "Agent chat request received",
            question_preview=question[:50],
        )
        response = agent.ask(question)
        log_with_context(
            app_logger,
            "INFO",
            "Agent chat response generated",
            response_length=len(str(response)),
        )
        return jsonify({"response": response})
    except Exception as e:
        log_with_context(app_logger, "ERROR", f"Agent chat failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/reports/<path:filename>", methods=["GET"])
def download_report(filename):
    """Serves the generated PDF risk reports."""
    reports_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"
    )
    os.makedirs(reports_dir, exist_ok=True)
    return send_from_directory(reports_dir, filename)


# ── MAP DATA ENDPOINT ──────────────────────────────────────────────────────────
@app.route("/api/map/data", methods=["GET"])
def get_map_data():
    """Returns geographic data for all active suppliers + factory hub."""
    from data.map_data import get_supplier_coords, FACTORY_HUB

    suppliers = get_supplier_coords()
    for s in suppliers:
        sid = s["supplier_id"]
        if sid in _active_overrides:
            s["current_delay_days"] = (
                s.get("current_delay_days", 0) + _active_overrides[sid]
            )

    return jsonify(
        {
            "hub": FACTORY_HUB,
            "suppliers": suppliers,
            "active_scenario": _active_scenario_id,
        }
    )


# ── SCENARIO ENDPOINTS ────────────────────────────────────────────────────────
def get_db_checksum():
    """Returns row counts for all tables to verify DB integrity."""
    conn = get_db_connection()
    counts = {
        "suppliers": conn.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0],
        "orders": conn.execute("SELECT COUNT(*) FROM purchase_orders").fetchone()[0],
        "status": conn.execute("SELECT COUNT(*) FROM supplier_status").fetchone()[0],
        "inventory": conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0],
    }
    conn.close()
    return counts


def _inject_chroma_event(event_data: dict):
    """Injects a scenario event into ChromaDB."""
    global _injected_chroma_ids, _saved_chroma_events
    try:
        import chromadb

        client = chromadb.PersistentClient(path=config.VECTOR_STORE_DIR)
        collection = client.get_collection("global_events")

        existing_ids = collection.get()["ids"]
        if event_data["event_id"] not in existing_ids:
            collection.add(
                ids=[event_data["event_id"]],
                documents=[event_data["description"]],
                metadatas=[{k: v for k, v in event_data.items() if k != "description"}],
            )
            _injected_chroma_ids.append(event_data["event_id"])
    except Exception as e:
        log_with_context(app_logger, "WARN", f"ChromaDB injection failed: {e}")


def _remove_chroma_event(event_id: str):
    """Removes an injected scenario event from ChromaDB."""
    try:
        import chromadb

        client = chromadb.PersistentClient(path=config.VECTOR_STORE_DIR)
        collection = client.get_collection("global_events")
        collection.delete(ids=[event_id])
    except Exception as e:
        log_with_context(app_logger, "WARN", f"ChromaDB removal failed: {e}")


@app.route("/api/scenario/trigger", methods=["POST"])
def trigger_scenario():
    """Applies a stress-test scenario to the dashboard."""
    global _active_scenario_id, _active_overrides, _injected_chroma_ids

    data = request.json or {}
    scenario_id = data.get("scenario_id")

    if not scenario_id:
        return jsonify({"error": "No scenario_id provided"}), 400
    if scenario_id not in SCENARIOS:
        return jsonify({"error": f"Unknown scenario: {scenario_id}"}), 400
    if _active_scenario_id:
        return jsonify({"error": "A scenario is already active. Reset it first."}), 409

    scenario = SCENARIOS[scenario_id]
    _active_scenario_id = scenario_id

    conn = get_db_connection()
    for country in scenario["affected_countries"]:
        rows = conn.execute(
            "SELECT supplier_id FROM suppliers WHERE country = ?", (country,)
        ).fetchall()
        for row in rows:
            _active_overrides[row["supplier_id"]] = scenario["delay_modifier"]
    conn.close()

    _inject_chroma_event(scenario["chroma_event"])

    log_with_context(
        app_logger,
        "INFO",
        f"Scenario triggered: {scenario_id}",
        affected=len(_active_overrides),
    )
    return jsonify(
        {
            "status": "active",
            "scenario": scenario["name"],
            "scenario_id": scenario_id,
            "affected_suppliers": len(_active_overrides),
            "description": scenario["chroma_event"]["description"],
        }
    )


@app.route("/api/scenario/reset", methods=["POST"])
def reset_scenario():
    """Resets all scenario overrides and restores DB integrity."""
    global _active_scenario_id, _active_overrides, _injected_chroma_ids

    if not _active_scenario_id:
        return jsonify({"error": "No active scenario to reset"}), 400

    for event_id in list(_injected_chroma_ids):
        _remove_chroma_event(event_id)

    _active_scenario_id = None
    _active_overrides = {}
    _injected_chroma_ids = []

    checksum = get_db_checksum()
    log_with_context(app_logger, "INFO", "Scenario reset complete", checksum=checksum)
    return jsonify({"status": "reset", "checksum": checksum})


@app.route("/api/scenario/status", methods=["GET"])
def get_scenario_status():
    """Returns current scenario state."""
    return jsonify(
        {
            "active": _active_scenario_id,
            "affected_suppliers": list(_active_overrides.keys()),
        }
    )


# ── SSE THOUGHT STREAM ENDPOINT ────────────────────────────────────────────────
@app.route("/api/stream/thoughts", methods=["GET"])
def thought_stream():
    """Server-Sent Events endpoint for real-time AI thought-trace."""

    def generate():
        q = queue.Queue(maxsize=50)
        _thought_queues.append(q)
        try:
            while True:
                try:
                    event = q.get(timeout=60)
                    yield f"data: {event}\n\n"
                except queue.Empty:
                    break
        finally:
            if q in _thought_queues:
                _thought_queues.remove(q)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── RUN SERVER ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log_with_context(
        app_logger,
        "INFO",
        f"Starting Flask server",
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
    )
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)
