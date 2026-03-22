# Resilienz.AI — Project Plan & High-Level Architecture 🏗️

> **Status:** ✅ COMPLETED — PEAK DEMO STATUS  
> **Last Updated:** 2026-03-22  

Resilienz.AI is designed to solve the "Reactive Gap" in manufacturing supply chains. This document outlines the core problem, the 4-layer architecture, and the project's evolution.

---

## 🔴 The Problem: Reactive vs. Proactive

### 1. The "Manual Detective" Drain
Procurement teams at SMEs often spend **30% to 40% of their time** manually chasing tracking numbers and refreshing supplier portals. This is a waste of high-value labor on low-value data entry.

### 2. The Transparency Gap
Internal ERP systems are static. They don't know about a **Suez Canal blockage** or a **Hamburg Port strike** until a human manually flags it. By then, the production line has often already stalled.

### 3. The "Bullwhip" Risk
A small delay in a €5 sensor can delay a €50,000 finished machine. Resilienz.AI provides the "Plan B" before the delay becomes a disaster.

---

## 🏗️ 4-Layer Architecture

| Layer | Component | Role |
|-------|-----------|------|
| **Layer 1** | **Data Ingestion** | The "Eyes & Ears": Pulls from CSVs (ERP), Supplier status, and Global news. |
| **Layer 2** | **AI Agent Brain**| The "Thinker": LLM (Gemini) evaluates facts vs. context and detects risks. |
| **Layer 3** | **Action** | The "Hands": Sends email alerts, generates PDF reports, and flags the UI. |
| **Layer 4** | **Dashboard** | The "Face": The modern Glassmorphism UI where humans verify AI findings. |

---

## 📁 Project Structure

```text
Resilienz.AI/
├── 📁 agent/          ← LLM reasoning logic, tools, and prompts.
├── 📁 api/            ← Flask backend server and SSE streaming.
├── 📁 dashboard/      ← The "Face": HTML/CSS/JS cockpit.
├── 📁 data/           ← Simulated ERP data (SQLite + ChromaDB).
├── 📁 documentation/  ← You are here: Master technical guide.
├── 📁 reports/        ← Generated PDF risk audits.
├── 📁 tests/          ← Unit and integration tests.
└── config.py          ← API keys and system settings.
```

---

## 📚 Technical Milestones

1.  **Phase 1: Foundations**: Data simulation and SQLite schema design.
2.  **Phase 2: The Action Logic**: Implementation of the 8 Python tools for R_agent.
3.  **Phase 3: The Brain**: Integrating Gemini and the Reasoning Loop.
4.  **Phase 4: The Interface**: Creating the modern digital cockpit.
5.  **Phase 5: Peak Demo**: Adding the Global Map, Stress-Tests, and SSE Thought-Trace.

---

## 🎯 Implementation Philiosphy

- **Think One Step Ahead**: Every AI reasoning step should be transparently visible to the human user (the **Thought-Trace**).
- **Safety First**: No direct database mutation during "What-If" simulations (the **Stress-Test Center**).
- **Graceful Degradation**: If an AI model fails, the system automatically switches to a fallback (the **Multi-LLM Switch**).
