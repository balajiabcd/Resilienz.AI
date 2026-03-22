# Resilienz.AI — Supply Chain Resilience Platform 🛡️🚀

**Resilienz.AI** is a proactive AI-driven procurement cockpit designed for German manufacturing SMEs. It monitors supply chain risks, investigates potential disruptions using a "Think-Act-Loop," and provides real-time transparency into the agent's reasoning.

## 🌟 Peak Demo Features (Added 2026-03-22)
- 🌍 **Global Risk Map**: Interactive Leaflet.js map visualizing logistical routes and risk hotspots.
- 🌋 **Stress-Test Scenario Center**: Zero-risk, in-memory simulations of global crises (Suez blockage, port strikes).
- 🧠 **AI Thought-Trace**: Real-time streaming of the agent's internal monologue via Server-Sent Events (SSE).

---

## 📂 Project Structure Overview

| Folder | Purpose |
|--------|---------|
| [**documentation/**](./documentation/1_project_plan.md) | **Master Library**: Full project history, architecture, and guide. |
| [agent/](./agent/README.md) | The AI brain (Multi-LLM) and its "hands" (Python tools). |
| [api/](./api/README.md) | Flask backend server with SSE streaming and scenario logic. |
| [dashboard/](./dashboard/README.md) | The "Face": Modern Glassmorphism Web UI. |
| [data/](./data/README.md) | Simulated data (SQLite + ChromaDB) and overrides layer. |
| [alerts/](./alerts/README.md) | Notification engine: SMTP Email & PDF Report generation. |

---

## 🚀 Quick Start (Demo Mode)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the backend (Port 5000)
python api/app.py

# 3. Open the cockpit
# Open dashboard/index.html in any modern web browser.
```

## 🧠 Technical Vision
Resilienz.AI follows a **Hybrid Database Strategy** (SQLite + ChromaDB) and a **Multi-LLM Resilience** architecture. It is built to ensure that critical manufacturing data is never a "black box," providing humans with full transparency during AI-driven risk audits.

---

*For detailed architectural deep-dives, see the [documentation/](./documentation/1_project_plan.md) folder.*
