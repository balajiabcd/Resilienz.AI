# Resilienz.AI — Agent Tools (Deep Dive) 🧰

This document details the "toolbox" available to the **R_agent**. Each tool is a Python function that the LLM uses to interact with the real-world data and take actions.

## 🎓 The Multi-Tool Strategy

The agent operates in a **Think-Act-Loop**:
1.  **Thinking**: The agent evaluates the user's request.
2.  **Tool Selection**: It chooses the most relevant function (e.g., `get_inventory_status`).
3.  **Action**: The Python tool executes (zero-token cost).
4.  **Observation**: The agent reads the result and updates its plan.

---

## 🧠 Real-Time Transparency (Thought-Trace)
A critical feature of the R_agent's tools is **Thought Emission**.
- **Internal Monologue**: The agent uses `emit_thought` to broadcast its reasoning steps to a **Server-Sent Events (SSE)** stream.
- **Visibility**: This allows the procurement manager to see *why* the agent is looking at a specific supplier before the final report is even generated.

---

## 🗃️ Available Tools

### 1. `get_delayed_orders()`
- **Purpose**: Retrieves all open purchase orders that are currently past their expected delivery date.
- **When to use**: At the start of every risk audit to identify initial targets.

### 2. `get_inventory_status(part_number)`
- **Purpose**: Returns stock quantity, days-of-cover, and daily consumption for a specific part.
- **Importance**: Helps the agent determine if a delay is a minor inconvenience or a production-stopping crisis.

### 3. `get_supplier_info(supplier_id)`
- **Purpose**: Fetches a supplier's reliability score, risk category, and alternative backup contacts.
- **Importance**: Allows the agent to assess vendor trustworthiness during a disruption.

### 4. `search_global_events(query)`
- **Purpose**: Performs a semantic search in **ChromaDB** for global news, port strikes, or geopolitical events.
- **Why Vector Search?**: Matches events by *meaning* (e.g., "port worker strike" vs "cargo disruption") rather than just keywords.

### 5. `calculate_risk_score(po_id)`
- **Purpose**: Computes a composite score (0-100) combining order criticality, supplier history, and current delay status.
- **Ranking**: Used to prioritize which risks appear at the top of the final audit report.

### 6. `get_alternative_supplier(part_number)`
- **Purpose**: Identifies the best pre-vetted alternative vendor for a specific component.
- **Actionable Insight**: Used by the agent to propose a "Plan B" when a primary route is blocked.

### 7. `send_alert(to, severity, body)`
- **Purpose**: Triggers a system alert or email to the procurement manager.
- **Side Effect**: This is an "action tool" that has a real-world impact.

### 8. `generate_risk_report(po_ids)`
- **Purpose**: Aggregates all findings into a structured executive brief.
- **Output**: The formatted Markdown you see in the dashboard.

---

## 📊 Summary Table

| Tool Name | Source | Key Insight Provided |
|-----------|--------|----------------------|
| `get_delayed_orders` | SQL | Identifies the "Red Flag" orders |
| `get_inventory_status` | SQL | Identifies "Production Line" impact |
| `search_global_events` | **Vector** | Identifies the "Root Cause" |
| `calculate_risk_score` | Logic | Identifies the "Priority" |
| `get_alternative_supplier`| SQL | Identifies the "Solution" |
