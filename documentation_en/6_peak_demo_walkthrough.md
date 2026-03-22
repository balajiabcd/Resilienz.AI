# Walkthrough — Resilienz.AI Peak Demo 🛡️✨

The Resilienz.AI project has been elevated to a "Peak Demo" state. This walkthrough documents the new high-impact features and the technical architecture that powers them.

## 🌟 New "Wow Factor" Features

### 1. **Global Risk Map**
A new interactive tab providing geographic context to the supply chain.
- **Visuals**: Centered on Europe with a custom **CartoDB Dark Matter** theme.
- **Data**: Connects every supplier to the **Amberg Factory Hub** via dynamic polylines.
- **Intelligence**: Markers pulse and color-shift based on real-time risk scores (Red/Amber/Green).
- **Interactivity**: Click any marker to see supplier health, active POs, and current delays.

### 2. **Autonomous Stress-Test Center**
Located within the Risk Audit tab, this allows "What-If" scenario simulations.
- **Scenarios**: Includes *Suez Canal Blockage*, *Port Strike (Hamburg)*, and *Energy Crisis*.
- **Mechanism**: **In-memory overrides**. Triggering a scenario simulates delays across categories without modifying the underlying SQLite database.
- **AI Integration**: Automatically injects a synthetic event into **ChromaDB**, allowing the agent to "reason" about the new crisis during the next audit.

### 3. **AI Thought-Trace**
A live monitor that reveals the agent's internal monologue.
- **Experience**: As the audit runs, a pulsing "🧠 AI is reasoning..." panel appears.
- **Detail**: Streams granular steps like "Detection: Found 12 delayed orders", "Investigation: Analyzing PO-2024-001", and "Synthesis: Generating report".
- **Tech**: Powered by **Server-Sent Events (SSE)** for zero-lag streaming.

---

## 🛠️ Technical Architecture

### **API Layer (`api/app.py`)**
- **In-Memory State**: Manages `_active_overrides` and `_thought_queues` to keep the demo fluid and safe.
- **SSE Server**: Implemented a custom event generator for real-time thought streaming.
- **Geographic Enrichment**: Uses `data/map_data.py` to map SQL data to coordinates.

### **Agent Logic (`auditing.py`)**
- **Context-Aware Emission**: The agent now "emits" its status at every major phase. If the Flask app is running, these are caught and streamed to the UI.

### **Frontend (`dashboard/`)**
- **Glassmorphism 2.0**: Updated CSS with smoother animations and pulsing indicators.
- **Map Integration**: Custom implementation using **Leaflet.js** with dark-theme overrides.

---

## 🚀 How to Demo

1.  **Baseline**: Show the "Global Map" and point out the healthy green routes.
2.  **Crisis**: Go to "Risk Audit", select **"Suez Canal Blockage"**, and click **Trigger**.
3.  **Observation**: Note the "Scenario Active" badge and the increase in "Delayed Orders" in the top bar.
4.  **Insight**: Click **"Start Audit"**. Watch the **Thought-Trace** as the agent detects the Suez crisis and investigates affected Asian suppliers.
5.  **Review**: Read the report—it will now incorporate the Suez disruption into its synthesis.
6.  **Recovery**: Click **"Reset Data"** to instantly return the dashboard to a clean, stable state.

---

## ✅ Current Project Situation
Resilienz.AI is now a state-of-the-art prototype that demonstrates proactive risk management with a premium, high-transparency user interface. It is ready for high-stakes stakeholder presentations.
