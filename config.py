"""
config.py — Resilienz.AI Central Configuration

This is the ONLY file where settings and keys are stored.
Every other file imports from here instead of hardcoding values.

WHY THIS MATTERS:
- Changing the database path? Change it here once, everywhere updates.
- Moving to a real API? Change it here once.
- Never scatter "magic values" across many files — that's how bugs are born.
"""

import os
from dotenv import load_dotenv

# Load any values from a .env file (if it exists)
# This keeps real secrets out of source code
load_dotenv()

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
VECTOR_STORE_DIR = os.path.join(DATA_DIR, "vector_store")

# ─── Database ────────────────────────────────────────────────────────────────
SQLITE_DB_PATH = os.path.join(DATA_DIR, "resilienz.db")

# ─── AI / LLM [OPENROUTER ONLY] ──────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Your dictionary of 20+ models (LATEST FREE MODELS - AUTO-ROUTING FIRST)
models = {
    1: "openrouter/free",  # Auto-routes to anything available!
    2: "google/gemini-2.0-flash:free",  # Highly reliable
    3: "meta-llama/llama-3.3-70b-instruct:free",  # Very powerful
    4: "deepseek/deepseek-r1:free",  # Excellent reasoning
    5: "google/gemini-2.0-flash-exp:free",
    6: "qwen/qwen3-next-80b-a3b-instruct:free",
    7: "qwen/qwen3-coder:free",
    8: "stepfun/step-3.5-flash:free",
    9: "nvidia/nemotron-3-super-120b-a12b:free",
    10: "nvidia/nemotron-3-nano-30b-a3b:free",
    11: "minimax/minimax-m2.5:free",
    12: "xiaomi/mimo-v2-flash:free",
    13: "arcee-ai/trinity-mini:free",
    14: "openai/gpt-oss-120b:free",
    15: "openai/gpt-oss-20b:free",
    16: "z-ai/glm-4.5-air:free",
    17: "google/gemma-3-27b-it:free",
    18: "mistralai/devstral-2-2505:free",
    19: "nvidia/nemotron-nano-12b-v2-vl:free",
    20: "nvidia/nemotron-nano-9b-v2:free",
    21: "mistralai/mistral-small-3.1-24b-instruct:free",
    22: "moonshotai/moonlight-5.5-aqua:free",
    23: "google/gemma-3n-e4b-it:free",
    24: "liquid/lfm-2.5-1.2b-instruct:free",
    25: "liquid/lfm-2.5-1.2b-thinking:free",
    26: "arcee-ai/trinity-large-preview:free",
    27: "upstage/solar-10.7b-instruct:free",
}

# Email Configuration
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", "agent@resilienz.ai")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "procurement@company.de")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# ─── Risk Scoring Thresholds ─────────────────────────────────────────────────
# These control when the agent escalates severity
RISK_CRITICAL_THRESHOLD = 70  # Score ≥ 70 → CRITICAL alert
RISK_HIGH_THRESHOLD = 45  # Score ≥ 45 → HIGH warning
RISK_MEDIUM_THRESHOLD = 20  # Score ≥ 20 → MEDIUM notice

# ─── Data Generation (Demo) ──────────────────────────────────────────────────
DATA_SEED = 42  # Ensures same data every time we regenerate
NUM_SUPPLIERS = 20
NUM_PURCHASE_ORDERS = 50
NUM_GLOBAL_EVENTS = 15

# ─── Flask Server ────────────────────────────────────────────────────────────
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
