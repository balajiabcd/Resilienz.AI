"""
data/map_data.py — Geographic Data for the Global Risk Map

Provides static city-to-coordinate mapping for all supplier cities.
No external API calls — purely static dictionary lookup.
"""

import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

FACTORY_HUB = {"name": "Factory HQ Amberg", "lat": 48.7324, "lon": 11.8528}

CITY_COORDS = {
    "Stuttgart": (48.7833, 9.1827),
    "Esslingen": (48.6219, 9.3093),
    "Lauffen": (49.0759, 9.1444),
    "Cologne": (50.9375, 6.9603),
    "Verl": (51.8833, 8.5167),
    "Waldkirch": (48.1119, 7.9717),
    "Mülheim": (51.4342, 6.8828),
    "Oppenweiler": (48.9811, 9.4572),
    "Ostfildern": (48.7257, 9.2593),
    "Detmold": (51.9356, 8.8832),
    "Blomberg": (51.9333, 9.0167),
    "Neuhausen": (48.6667, 9.2833),
    "Gothenburg": (57.7089, 11.9746),
    "Dublin": (53.3498, -6.2603),
    "Cleveland": (41.4993, -81.6944),
    "Tokyo": (35.6762, 139.6503),
    "Rueil-Malmaison": (48.8770, 2.1912),
    "Zurich": (47.3769, 8.5417),
    "Nuremberg": (49.4521, 11.0767),
}


def get_db_connection():
    conn = sqlite3.connect(config.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_risk_level(reliability_score: float) -> str:
    if reliability_score >= 0.90:
        return "LOW"
    elif reliability_score >= 0.80:
        return "MEDIUM"
    else:
        return "HIGH"


def get_supplier_coords() -> list:
    conn = get_db_connection()

    suppliers = conn.execute("""
        SELECT
            s.supplier_id,
            s.supplier_name,
            s.city,
            s.country,
            s.reliability_score,
            s.risk_category
        FROM suppliers s
    """).fetchall()

    active_pos = conn.execute("""
        SELECT supplier_id, COUNT(*) as po_count
        FROM purchase_orders
        WHERE status != 'DELIVERED'
        GROUP BY supplier_id
    """).fetchall()
    po_count_map = {row["supplier_id"]: row["po_count"] for row in active_pos}

    current_delays = conn.execute("""
        SELECT supplier_id, SUM(delay_days) as total_delay
        FROM supplier_status
        WHERE delay_days > 0
        GROUP BY supplier_id
    """).fetchall()
    delay_map = {row["supplier_id"]: row["total_delay"] for row in current_delays}

    conn.close()

    result = []
    for s in suppliers:
        city_key = s["city"]
        coords = CITY_COORDS.get(city_key)
        if not coords:
            continue

        supplier_id = s["supplier_id"]
        result.append(
            {
                "supplier_id": supplier_id,
                "name": s["supplier_name"],
                "city": s["city"],
                "country": s["country"],
                "lat": coords[0],
                "lon": coords[1],
                "risk_category": s["risk_category"]
                or get_risk_level(s["reliability_score"]),
                "reliability_score": s["reliability_score"],
                "active_pos": po_count_map.get(supplier_id, 0),
                "current_delay_days": delay_map.get(supplier_id, 0),
            }
        )

    return result
