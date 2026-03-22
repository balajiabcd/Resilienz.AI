# Resilienz.AI — Complete Feature & Usage Guide 🛡️

**Resilienz.AI** is a proactive AI-driven procurement cockpit designed for German manufacturing SMEs. It monitors supply chain risks, investigates potential disruptions, and provides actionable insights to prevent production downtime.

---

## 🚀 1. Core Capabilities

### **Proactive Risk Monitoring**
- **Automated Scanning**: Constantly monitors **SQLite** (purchase orders, inventory) and **ChromaDB** (global news/events).
- **Hybrid Reasoning**: Uses Python for high-speed data processing and LLMs (Gemini/OpenRouter) for complex situational analysis.
- **Criticality Detection**: Identifies orders where expected delivery dates, current inventory, and external threats create a high-risk scenario.

### **Autonomous AI Agent (R_agent)**
- **Self-Correcting**: Uses a "Thought-Trace" process to chain together data fetching, analysis, and report generation.
- **Flexible Intelligence**: Employs an **LLMSwitch** strategy, automatically falling back to alternative models if rate limits are hit or errors occur.
- **Multimodal Output**: Generates detailed Markdown reports and can produce PDF exports for stakeholder review.

---

## 🎨 2. The Dashboard (Visual Cockpit)

### **Metrics Bar (Real-Time)**
- **Active Suppliers**: Count of vendors in the system.
- **In-Transit Orders**: Total volume of open purchase orders.
- **Delayed Orders**: **(Critical)** Count of orders currently behind schedule.
- **Parts Catalog**: Total variety of components managed.

### **Global Risk Map (New)**
- **Geographic Context**: Visualizes the entire supply chain footprint.
- **Amberg Factory Hub**: Central point for all logistics calculations.
- **Dynamic Polylines**: Lines connect suppliers to the factory, changing color/style based on current risk levels.
- **Pulsing Hotspots**: High-risk areas are visually highlighted with amber/red pulse animations.

---

## 🌋 3. Stress-Test Scenario Center

Allows procurement teams to simulate global events without corrupting live data.

| Scenario | Effect | Affected Regions |
|----------|--------|------------------|
| **Suez Blockage** | +14 Day Delay | Japan, China, S. Korea |
| **Port Strike** | +7 Day Delay | Germany (Hamburg) |
| **Energy Crisis** | +4 Day Delay | Germany (Nationwide) |

- **Mechanism**: Simulations are handled **in-memory**. They update dashboard metrics and AI audits instantly but do not write to the permanent SQLite database.
- **Reset**: A single click restores the dashboard to the baseline "clean" state.

---

## 💬 4. Interactive Collaboration

### **Scientific Risk Audit**
- **Process**: Trigger an autonomous audit loop that decomposes the entire supply chain into individual investigations.
- **Transparency**: Follow the **AI Thought-Trace** as it moves from *Detection* to *Synthesis*.
- **Report**: Receive a professional executive summary with a table of "at-risk" orders and recommended mitigations.

### **R_agent Chat**
- **Natural Language**: 💬 Ask questions like *"Is PO-2024-001 safe?"* or *"How much buffer stock do we have for sensors?"*
- **Contextual Awareness**: The agent has access to real-time inventory levels, supplier reliability scores, and current headlines.

---

## 🛠️ 5. Usage Guide (Quick Start)

### **A. Initial Setup**
1.  **Launch Backend**: Run `python api/app.py`.
2.  **Open Dashboard**: Open `dashboard/index.html` in any modern web browser.
3.  **Check Status**: Ensure the "System Live" green pulse is visible in the sidebar.

### **B. Performing an Audit**
1.  Navigate to the **Risk Audit** tab.
2.  Click **🚀 Start Audit**.
3.  Watch the **Thought-Trace** panel appear above the results.
4.  Once the "✅ Reasoning complete" status appears, read the Markdown report.

### **C. Running a Stress-Test**
1.  In the Audit tab, use the **Scenario Selector**.
2.  Choose a crisis (e.g., *Port Strike — Hamburg*).
3.  Click **⚡ Trigger**.
4.  Switch to the **Global Map** tab to see affected German routes turn red.
5.  Check the **Metrics Bar** to see the "Delayed Orders" count increase.

### **D. Conversing with R_agent**
1.  Navigate to the **💬 Chat** tab.
2.  Type your question in the bottom bar.
3.  R_agent will analyze current data and respond within 2-5 seconds.

---

## ✅ Summary of Tech Stack
-   **Frontend**: Vanilla HTML/CSS/JS (Glassmorphism theme) + Leaflet.js.
-   **Backend**: Flask (Python) with SSE (Server-Sent Events) for real-time streaming.
-   **Data**: SQLite (Structured) + ChromaDB (Unstructured/Vector).
-   **AI**: Gemini Flash (Primary) + OpenRouter Fallbacks.
