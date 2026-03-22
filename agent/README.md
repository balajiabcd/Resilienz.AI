# Agent Folder — The Brain & Tools 🧠🧰

The `agent/` directory contains the core intelligence of **R_agent**. This is where raw data meets high-level reasoning.

## 📄 Components

| Component | Purpose |
|-----------|---------|
| `tools.py` | The agent's "hands" — 8 Python functions for SQL, Vector DB, and report generation. |
| `llm/` | **The Multi-LLM Switch**: Pluggable drivers for Gemini & OpenRouter to ensure uptime. |
| `brain.py` | The orchestrator that manages the **Think-Act-Loop**. |
| `prompts.py` | The agent's "Constitution"—defines personality, reasoning phases, and boundaries. |

## 🌟 Peak Demo: Thought Emission
The agent now includes **Real-Time Instrumentation**. During its reasoning loop, it uses `emit_thought` to broadcast its internal status to the backend. This transparency allows the human user to follow the agent's work step-by-step.

---

*For tool-specific details, refer to [4_agent_tools.md](../documentation/4_agent_tools.md).*
