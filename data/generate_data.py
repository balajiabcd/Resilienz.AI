"""
data/generate_data.py — Resilienz.AI Demo Data Generator

==============================================================
WHAT THIS SCRIPT DOES (Read this carefully!)
==============================================================
This script creates ALL the demo data for our project.
It generates realistic-looking but 100% fake data, then:
  1. Saves 5 CSV files (human-readable, inspectable in Excel)
  2. Loads the structured data into SQLite (our regular DB)
  3. Loads the events data into ChromaDB (our vector DB)

WHY GENERATE DATA INSTEAD OF USING REAL DATA?
  - No real SAP/ERP system needed for the demo
  - We can CONTROL which scenarios exist (inject delays, crises)
  - Reproducible: same seed = same data every time
  - No privacy/GDPR issues

HOW TO RUN:
  python data/generate_data.py

WHAT YOU'LL SEE AFTER RUNNING:
  data/
  ├── suppliers.csv
  ├── purchase_orders.csv
  ├── supplier_status.csv
  ├── inventory.csv
  ├── global_events.csv
  ├── resilienz.db          ← SQLite database
  └── vector_store/         ← ChromaDB files
==============================================================
"""

import os
import sys
import random
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

# ── Make sure we can import config from the parent directory ──────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# ── Setup ─────────────────────────────────────────────────────────────────────
fake = Faker("de_DE")           # German locale for realistic names
Faker.seed(config.DATA_SEED)
random.seed(config.DATA_SEED)

os.makedirs(config.DATA_DIR, exist_ok=True)
os.makedirs(config.VECTOR_STORE_DIR, exist_ok=True)

TODAY = datetime.now().date()


# ==============================================================================
# STEP 1: Generate suppliers.csv
# ==============================================================================
def generate_suppliers() -> pd.DataFrame:
    """
    Creates a master list of suppliers.
    Each supplier has a reliability score and a backup alternative.

    LESSON: We build suppliers FIRST because purchase orders reference them.
    This is called "maintaining referential integrity" — child records (orders)
    must point to valid parent records (suppliers).
    """
    print("📦 Generating suppliers...")

    german_companies = [
        ("Bosch Rexroth GmbH", "Stuttgart", "DE"),
        ("Festo AG & Co. KG", "Esslingen", "DE"),
        ("Schunk GmbH", "Lauffen", "DE"),
        ("igus GmbH", "Cologne", "DE"),
        ("Beckhoff Automation", "Verl", "DE"),
        ("SICK AG", "Waldkirch", "DE"),
        ("Turck GmbH", "Mülheim", "DE"),
        ("Murrelektronik GmbH", "Oppenweiler", "DE"),
        ("Pilz GmbH", "Ostfildern", "DE"),
        ("Weidmüller GmbH", "Detmold", "DE"),
        ("Phoenix Contact GmbH", "Blomberg", "DE"),
        ("Balluff GmbH", "Neuhausen", "DE"),
        # International suppliers (higher risk profile)
        ("SKF AB", "Gothenburg", "SE"),
        ("Eaton Corporation", "Dublin", "IE"),
        ("Parker Hannifin", "Cleveland", "US"),
        ("SMC Corporation", "Tokyo", "JP"),
        ("Schneider Electric", "Rueil-Malmaison", "FR"),
        ("ABB Ltd", "Zurich", "CH"),
        ("Siemens Industry", "Nuremberg", "DE"),
        ("Mitsubishi Electric", "Tokyo", "JP"),
    ]

    suppliers = []
    ids = [f"SUP-{str(i).zfill(3)}" for i in range(1, len(german_companies) + 1)]

    for i, (name, city, country) in enumerate(german_companies):
        # Domestic German suppliers tend to be more reliable
        base_reliability = 0.92 if country == "DE" else 0.78
        
        # Calculate reliability - we've broken this down into steps 
        # to clear up a type-checking ambiguity with round()
        upper_bound = min(base_reliability + 0.07, 0.99)
        raw_reliability = random.uniform(base_reliability - 0.08, upper_bound)
        reliability = round(raw_reliability, 2)

        # Calculate average delay similarly
        if reliability < 0.85:
            raw_delay = random.uniform(0.0, 5.0)
        else:
            raw_delay = random.uniform(0.0, 1.5)
        avg_delay = round(raw_delay, 1)
 
        if reliability >= 0.90:
            risk_cat = "LOW"
        elif reliability >= 0.80:
            risk_cat = "MEDIUM"
        else:
            risk_cat = "HIGH"

        # Each supplier has a random alternative (not itself)
        alt_idx = random.choice([j for j in range(len(ids)) if j != i])

        suppliers.append({
            "supplier_id":            ids[i],
            "supplier_name":          name,
            "country":                country,
            "city":                   city,
            "reliability_score":      reliability,
            "avg_delay_days":         avg_delay,
            "risk_category":          risk_cat,
            "alternative_supplier_id": ids[alt_idx],
            "contact_email":          f"orders@{name.lower().split()[0]}.com",
            "payment_terms_days":     random.choice([30, 45, 60]),
        })

    df = pd.DataFrame(suppliers)
    df.to_csv(os.path.join(config.DATA_DIR, "suppliers.csv"), index=False)
    print(f"   ✅ Created {len(df)} suppliers")
    return df


# ==============================================================================
# STEP 2: Generate purchase_orders.csv
# ==============================================================================
def generate_purchase_orders(suppliers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates open purchase orders referencing the suppliers.

    KEY LEARNING MOMENT:
    We intentionally inject specific scenarios into the data:
      - Some orders are HIGH criticality with upcoming deadlines
      - Some are MEDIUM, some LOW
    This lets the agent demonstrate its full range of behavior.
    """
    print("📋 Generating purchase orders...")

    parts_catalog = [
        ("AX-7741-B", "Hydraulic valve 12mm",         "HIGH"),
        ("PL-3302-A", "Linear guide rail 500mm",       "HIGH"),
        ("SN-9981-C", "Proximity sensor NPN 24V",      "MEDIUM"),
        ("CB-1145-D", "Control cable 10m shielded",     "LOW"),
        ("MT-5567-E", "Servo motor 400W",              "HIGH"),
        ("BG-2230-F", "Ball bearing 6205-2RS",         "LOW"),
        ("PC-8812-G", "Pneumatic cylinder 80mm stroke", "HIGH"),
        ("FT-4490-H", "Flow transmitter 4-20mA",       "MEDIUM"),
        ("RL-6623-I", "Relay module 24V DIN",          "LOW"),
        ("GK-7750-J", "Rotary encoder 1024ppr",        "MEDIUM"),
        ("TP-1130-K", "Temperature probe PT100",       "MEDIUM"),
        ("VS-3348-L", "Vision sensor 2MP",             "HIGH"),
        ("PP-9920-M", "Pressure regulator 0-10 bar",   "MEDIUM"),
        ("EV-5514-N", "Solenoid valve 24VDC",          "HIGH"),
        ("DC-2267-O", "DC/DC converter 24V/5V",        "LOW"),
    ]

    production_lines = ["LINE-A1", "LINE-A2", "LINE-A3", "LINE-B1", "LINE-B2", "LINE-C1"]
    supplier_ids = suppliers_df["supplier_id"].tolist()

    orders = []
    for i in range(1, config.NUM_PURCHASE_ORDERS + 1):
        # 🚨 FORCE PO-2024-001 to be AX-7741-B for the demo risk scenario
        if i == 1:
            part = parts_catalog[0]
        else:
            part = random.choice(parts_catalog)
        supplier_id = random.choice(supplier_ids)
        order_date = TODAY - timedelta(days=random.randint(10, 60))
        lead_time   = random.randint(14, 45)
        expected_delivery = order_date + timedelta(days=lead_time)

        orders.append({
            "po_id":             f"PO-2024-{str(i).zfill(3)}",
            "supplier_id":       supplier_id,
            "supplier_name":     suppliers_df.loc[suppliers_df["supplier_id"] == supplier_id, "supplier_name"].values[0],
            "part_number":       part[0],
            "part_description":  part[1],
            "quantity_ordered":  random.randint(50, 1000),
            "unit_price_eur":    round(random.uniform(1.5, 250.0), 2),
            "order_date":        order_date.isoformat(),
            "expected_delivery": expected_delivery.isoformat(),
            "destination_line":  random.choice(production_lines),
            "criticality":       part[2],
            "status":            random.choices(["OPEN", "PARTIAL"], weights=[0.85, 0.15])[0],
        })

    df = pd.DataFrame(orders)
    df.to_csv(os.path.join(config.DATA_DIR, "purchase_orders.csv"), index=False)
    print(f"   ✅ Created {len(df)} purchase orders")
    return df


# ==============================================================================
# STEP 3: Generate supplier_status.csv
# ==============================================================================
def generate_supplier_status(orders_df: pd.DataFrame, suppliers_df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates the real-time status update for each open order.

    THIS IS WHERE THE DRAMA HAPPENS.
    We inject specific dangerous scenarios to make the demo powerful:
      - Scenario A: HIGH criticality order, 7+ day delay
      - Scenario B: MEDIUM criticality, 3 day delay
      - Scenario C: On time (so the agent also knows when NOT to panic)
    """
    print("🚦 Generating supplier status (injecting delay scenarios)...")

    delay_reasons = [
        "Port congestion in Hamburg",
        "Customs clearance delay",
        "Production capacity issue at supplier",
        "Raw material shortage (steel)",
        "Transport provider overload",
        "Quality hold — re-inspection required",
        "Weather-related logistics disruption",
        "Dockworkers' strike — North German ports",
        "Energy shortage affecting production",
        "Component shortage from sub-supplier",
    ]

    statuses = []
    for _, order in orders_df.iterrows():
        supplier = suppliers_df[suppliers_df["supplier_id"] == order["supplier_id"]].iloc[0]

        # Lower reliability suppliers are more likely to be delayed
        delay_probability = 1 - supplier["reliability_score"]
        is_delayed = random.random() < (delay_probability + 0.15)  # +15% to make demo interesting

        if is_delayed:
            delay_days = random.randint(2, 12)
            reason = random.choice(delay_reasons)
            confidence = random.choice(["MEDIUM", "LOW"])
        else:
            delay_days = 0
            reason = ""
            confidence = "HIGH"

        expected = datetime.fromisoformat(order["expected_delivery"])
        confirmed = expected + timedelta(days=delay_days)

        statuses.append({
            "po_id":               order["po_id"],
            "supplier_id":         order["supplier_id"],
            "last_update":         (TODAY - timedelta(days=random.randint(0, 3))).isoformat(),
            "confirmed_delivery":  confirmed.date().isoformat(),
            "delay_days":          delay_days,
            "delay_reason":        reason,
            "confidence_level":    confidence,
            "tracking_number":     f"DHL-{random.randint(1000000, 9999999)}",
            "current_location":    random.choice([
                "Hamburg Port", "Frankfurt Hub", "Supplier Warehouse",
                "In Transit DE", "Rotterdam Port", "In Transit NL", "Delivered"
            ]),
        })

    # ── INJECT GUARANTEED CRITICAL SCENARIO (so demo always has drama) ────────
    # Force PO-2024-001 to be a crisis: HIGH criticality, 8-day delay
    critical_idx = statuses[0]
    critical_idx["delay_days"]       = 8
    critical_idx["confirmed_delivery"] = (TODAY + timedelta(days=8)).isoformat()
    critical_idx["delay_reason"]     = "Dockworkers' strike — North German ports"
    critical_idx["confidence_level"] = "LOW"
    critical_idx["current_location"] = "Hamburg Port"
    print("   🚨 Injected CRITICAL scenario into PO-2024-001")

    df = pd.DataFrame(statuses)
    df.to_csv(os.path.join(config.DATA_DIR, "supplier_status.csv"), index=False)
    print(f"   ✅ Created {len(df)} supplier status records")
    return df


# ==============================================================================
# STEP 4: Generate inventory.csv
# ==============================================================================
def generate_inventory(orders_df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates stock level records for every part in our orders.

    KEY CONCEPT: 'days_of_cover' is the critical number.
    If days_of_cover < delay_days → production WILL stop.
    The agent uses this to calculate true urgency.
    """
    print("🏭 Generating inventory levels...")

    parts = orders_df[["part_number", "part_description"]].drop_duplicates()
    inventory = []

    for _, part in parts.iterrows():
        daily_consumption = round(random.uniform(5.0, 50.0), 1)
        stock_qty = random.randint(10, 500)
        days_cover = round(stock_qty / daily_consumption, 1)
        min_stock  = int(daily_consumption * random.randint(3, 7))

        inventory.append({
            "part_number":       part["part_number"],
            "part_description":  part["part_description"],
            "stock_quantity":    stock_qty,
            "min_stock_level":   min_stock,
            "days_of_cover":     days_cover,
            "daily_consumption": daily_consumption,
            "warehouse_location": f"RACK-{random.choice('ABCD')}-{random.randint(1,20)}",
        })

    # ── INJECT LOW STOCK for the critical part (AX-7741-B) ───────────────────
    for item in inventory:
        if item["part_number"] == "AX-7741-B":
            item["stock_quantity"]  = 30
            item["daily_consumption"] = 12.0
            item["days_of_cover"]   = 2.5   # Only 2.5 days! Delay is 8 days → PANIC
            item["min_stock_level"] = 36
            print("   🚨 Injected LOW STOCK for AX-7741-B (2.5 days cover)")
            break

    df = pd.DataFrame(inventory)
    df.to_csv(os.path.join(config.DATA_DIR, "inventory.csv"), index=False)
    print(f"   ✅ Created {len(df)} inventory records")
    return df


# ==============================================================================
# STEP 5: Generate global_events.csv
# ==============================================================================
def generate_global_events() -> pd.DataFrame:
    """
    Creates external disruption events (news-style data).

    CRITICAL LEARNING: This is the data that will be stored in the VECTOR DB.
    Why? Because the agent needs to SEMANTICALLY SEARCH these events.
    Example: "disruptions near Hamburg" should match "North German port strike".
    A regular SQL LIKE query would miss that — a vector search won't.
    """
    print("🌍 Generating global events...")

    events = [
        # ── Active, relevant events ───────────────────────────────────────────
        {
            "event_id":           "EVT-001",
            "event_date":         (TODAY - timedelta(days=3)).isoformat(),
            "event_type":         "PORT_STRIKE",
            "location":           "Hamburg, Germany",
            "affected_countries": "DE, NL, BE, PL",
            "severity":           "HIGH",
            "estimated_delay_days": 7,
            "description":        (
                "Dockworkers at the Port of Hamburg have entered their third day of strike action, "
                "severely disrupting container handling. GDL union members are demanding a 15% wage increase. "
                "Approximately 900,000 TEU of cargo is affected. Expected resolution: 5–10 days. "
                "Alternative routing via Bremerhaven or Rotterdam is being explored by logistics providers."
            ),
            "source":   "Reuters",
            "resolved": False,
        },
        {
            "event_id":           "EVT-002",
            "event_date":         (TODAY - timedelta(days=1)).isoformat(),
            "event_type":         "ENERGY_SHORTAGE",
            "location":           "Germany (Nationwide)",
            "affected_countries": "DE",
            "severity":           "MEDIUM",
            "estimated_delay_days": 3,
            "description":        (
                "Germany faces elevated energy prices following cold snap. Several industrial suppliers "
                "in Baden-Württemberg and Bavaria have reduced production output by 20–30% due to energy costs. "
                "Mechanical components and precision parts most affected. Forecast: 3-5 days impact."
            ),
            "source":   "Handelsblatt",
            "resolved": False,
        },
        {
            "event_id":           "EVT-003",
            "event_date":         (TODAY - timedelta(days=5)).isoformat(),
            "event_type":         "CUSTOMS_DELAY",
            "location":           "Rotterdam, Netherlands",
            "affected_countries": "NL, DE, BE",
            "severity":           "MEDIUM",
            "estimated_delay_days": 4,
            "description":        (
                "IT system outage at Rotterdam Customs has caused significant processing backlogs. "
                "Approximately 2,400 containers are awaiting clearance. "
                "Imports from Asia and Americas most affected. Partial recovery expected within 48 hours."
            ),
            "source":   "Port of Rotterdam Authority",
            "resolved": False,
        },
        {
            "event_id":           "EVT-004",
            "event_date":         (TODAY - timedelta(days=10)).isoformat(),
            "event_type":         "WEATHER",
            "location":           "North Sea",
            "affected_countries": "DE, DK, NO, SE",
            "severity":           "LOW",
            "estimated_delay_days": 2,
            "description":        (
                "Storm Friederike has caused 24–48 hour delays to ferry services crossing the North Sea. "
                "Trucking from Scandinavia experiencing minor delays at border crossings. "
                "Situation normalising. Impact: primarily low-volume automotive parts from Sweden and Denmark."
            ),
            "source":   "DWD Weather Service",
            "resolved": True,
        },
        {
            "event_id":           "EVT-005",
            "event_date":         (TODAY - timedelta(days=2)).isoformat(),
            "event_type":         "SUPPLIER_BANKRUPTCY",
            "location":           "Osaka, Japan",
            "affected_countries": "JP, KR, CN",
            "severity":           "HIGH",
            "estimated_delay_days": 30,
            "description":        (
                "Yamada Precision Parts, a mid-tier Japanese electronics component manufacturer, "
                "has filed for civil rehabilitation (bankruptcy protection). "
                "The company supplies specialty sensors and encoders to European OEMs. "
                "Customers are advised to map exposure immediately and identify alternative sources."
            ),
            "source":   "Nikkei Business",
            "resolved": False,
        },
        {
            "event_id":           "EVT-006",
            "event_date":         (TODAY - timedelta(days=7)).isoformat(),
            "event_type":         "GEOPOLITICAL",
            "location":           "Suez Canal",
            "affected_countries": "GLOBAL",
            "severity":           "CRITICAL",
            "estimated_delay_days": 14,
            "description":        (
                "Continued Houthi attacks in the Red Sea have forced major shipping lines to reroute "
                "vessels around the Cape of Good Hope. This adds approximately 10–14 days to Asia-Europe "
                "transit times and increases freight costs by 200–300%. Electronics, textiles, and machinery "
                "from China, India, and Southeast Asia most affected. No near-term resolution expected."
            ),
            "source":   "Lloyd's List",
            "resolved": False,
        },
        {
            "event_id":           "EVT-007",
            "event_date":         (TODAY - timedelta(days=4)).isoformat(),
            "event_type":         "RAIL_DISRUPTION",
            "location":           "Frankfurt, Germany",
            "affected_countries": "DE, CH, AT",
            "severity":           "MEDIUM",
            "estimated_delay_days": 3,
            "description":        (
                "Deutsche Bahn infrastructure fault between Frankfurt and Mannheim has caused significant "
                "freight rail delays on the Rhine corridor. Automotive parts and chemical shipments diverted "
                "to road transport, increasing costs. Expected repair completion: 5 days."
            ),
            "source":   "Deutsche Bahn AG",
            "resolved": False,
        },
        {
            "event_id":           "EVT-008",
            "event_date":         (TODAY - timedelta(days=14)).isoformat(),
            "event_type":         "RAW_MATERIAL_SHORTAGE",
            "location":           "Czech Republic",
            "affected_countries": "CZ, DE, SK",
            "severity":           "MEDIUM",
            "estimated_delay_days": 5,
            "description":        (
                "Steel sheet shortage in Central Europe following closure of a major Czech steel plant "
                "for emergency maintenance. Automotive stamping suppliers in Germany and Slovakia reporting "
                "2–3 week delivery extensions for steel-dependent components."
            ),
            "source":   "EUROMETAL Industry Report",
            "resolved": False,
        },
        # ── Resolved events (historical context) ──────────────────────────────
        {
            "event_id":           "EVT-009",
            "event_date":         (TODAY - timedelta(days=21)).isoformat(),
            "event_type":         "PORT_CONGESTION",
            "location":           "Bremerhaven, Germany",
            "affected_countries": "DE",
            "severity":           "LOW",
            "estimated_delay_days": 2,
            "description":        (
                "Temporary congestion at Bremerhaven AutoTerminal due to vessel bunching. "
                "Automotive imports delayed 2–3 days. Situation resolved after additional "
                "berth capacity was made available."
            ),
            "source":   "BLG Logistics",
            "resolved": True,
        },
        {
            "event_id":           "EVT-010",
            "event_date":         (TODAY - timedelta(days=30)).isoformat(),
            "event_type":         "FACTORY_FIRE",
            "location":           "Lyon, France",
            "affected_countries": "FR, DE",
            "severity":           "HIGH",
            "estimated_delay_days": 45,
            "description":        (
                "Fire at Renault Flins component warehouse destroyed significant stock of hydraulic "
                "and pneumatic assemblies. French automotive suppliers are diverting parts to alternative "
                "customers. German manufacturers sourcing from French sub-contractors advised to assess exposure."
            ),
            "source":   "Le Monde Industrie",
            "resolved": False,
        },
    ]

    df = pd.DataFrame(events)
    df.to_csv(os.path.join(config.DATA_DIR, "global_events.csv"), index=False)
    print(f"   ✅ Created {len(df)} global events")
    return df


# ==============================================================================
# STEP 6: Load structured data into SQLite
# ==============================================================================
def load_into_sqlite(suppliers_df, orders_df, status_df, inventory_df):
    """
    Takes our DataFrames and saves them into an SQLite database.

    WHY USE SQLITE AND CSV?
    - CSV = human readable, easy to share and inspect in Excel
    - SQLite = fast queries, joins, filtering — what the agent uses at runtime
    Both hold the same data. CSV is for humans, SQLite is for the agent.
    """
    print("\n🗃️  Loading data into SQLite...")
    conn = sqlite3.connect(config.SQLITE_DB_PATH)

    suppliers_df.to_sql("suppliers",        conn, if_exists="replace", index=False)
    orders_df.to_sql("purchase_orders",     conn, if_exists="replace", index=False)
    status_df.to_sql("supplier_status",     conn, if_exists="replace", index=False)
    inventory_df.to_sql("inventory",        conn, if_exists="replace", index=False)

    conn.close()
    print(f"   ✅ SQLite database created at: {config.SQLITE_DB_PATH}")


# ==============================================================================
# STEP 7: Load events into ChromaDB (Vector Database)
# ==============================================================================
def load_into_vector_db(events_df: pd.DataFrame):
    """
    Stores the global events in ChromaDB as vector embeddings.

    HOW CHROMADB WORKS:
    1. You give it text (the event description)
    2. It converts text to a vector (list of numbers representing meaning)
    3. When you search, it converts your query to a vector too
    4. It finds stored vectors that are mathematically "close" to your query
    5. "Close" vectors = similar meaning → that's semantic search!

    ChromaDB uses a simple built-in embedding model by default.
    In production, you'd use Gemini embeddings for better accuracy.
    """
    print("\n🧠 Loading events into ChromaDB (Vector DB)...")

    try:
        import chromadb
        client = chromadb.PersistentClient(path=config.VECTOR_STORE_DIR)

        # Delete existing collection if re-running (clean slate)
        try:
            client.delete_collection("global_events")
        except Exception:
            pass

        collection = client.create_collection(
            name="global_events",
            metadata={"description": "Global supply chain disruption events for Resilienz.AI"}
        )

        collection.add(
            ids=events_df["event_id"].tolist(),
            documents=events_df["description"].tolist(),   # The text ChromaDB embeds
            metadatas=events_df.drop(columns=["description"]).to_dict("records"),  # Extra info
        )

        print(f"   ✅ {len(events_df)} events loaded into ChromaDB at: {config.VECTOR_STORE_DIR}")
        print("   ✅ Vector embeddings created — ready for semantic search!")

    except ImportError:
        print("   ⚠️  ChromaDB not installed yet. Run: pip install chromadb")
        print("   ⚠️  Skipping vector DB load — will work after install.")


# ==============================================================================
# MAIN — Run everything in order
# ==============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  RESILIENZ.AI — Data Generation Script")
    print("=" * 60)
    print(f"  Seed:     {config.DATA_SEED}  (change in config.py for different data)")
    print(f"  Suppliers:{config.NUM_SUPPLIERS}")
    print(f"  Orders:   {config.NUM_PURCHASE_ORDERS}")
    print(f"  Events:   {config.NUM_GLOBAL_EVENTS}")
    print("=" * 60 + "\n")

    # Generate all DataFrames
    suppliers_df  = generate_suppliers()
    orders_df     = generate_purchase_orders(suppliers_df)
    status_df     = generate_supplier_status(orders_df, suppliers_df)
    inventory_df  = generate_inventory(orders_df)
    events_df     = generate_global_events()

    # Persist to databases
    load_into_sqlite(suppliers_df, orders_df, status_df, inventory_df)
    load_into_vector_db(events_df)

    print("\n" + "=" * 60)
    print("  ✅ ALL DATA GENERATED SUCCESSFULLY!")
    print("=" * 60)
    print("\n  Files created:")
    for f in ["suppliers.csv", "purchase_orders.csv", "supplier_status.csv",
              "inventory.csv", "global_events.csv", "resilienz.db"]:
        full_path = os.path.join(config.DATA_DIR, f)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"    📄 {f} ({size:,} bytes)")
    print(f"    📁 vector_store/ (ChromaDB)")
    print("\n  Next step: Run the agent!")
    print("  → python agent/brain.py")
