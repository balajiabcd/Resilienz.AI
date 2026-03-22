# API Folder — The Connection Layer 🔌📡

The `api/` directory connects the **AI Agent** to the **Dashboard** and external actors through a professional-grade Flask backend.

## 📄 Key Components

| File | Role |
|------|------|
| `app.py` | The **Flask Server**: Root of the risk cockpit. Manages endpoints for audits, chat, and data. |
| `sse_server.py` | The **Thought Streamer**: A dedicated SSE (Server-Sent Events) generator that broadcasts the AI's "internal monologue." |

## 🧪 Peak Demo: The Scenario Layer
The backend implements a **Dynamic Override Layer**. It manages the state of the "Stress-Test Center" in-memory.
- **`_active_overrides`**: Stores simulated delays from scenarios (Suez, Hamburg, etc.).
- **Data Merging**: Intercepts requests for supplier data and merges SQL facts with active overrides before passing them back to the UI or Agent.

---

*For detailed API documentation, refer to the [5_resilienz_ai_complete_guide.md](../documentation/5_resilienz_ai_complete_guide.md) documentation.*
