# API-Ordner — Die Verbindungs-Schicht 🔌📡

Der Ordner `api/` verbindet den **KI-Agenten** mit dem **Dashboard** über einen Flask-Server.

## 📄 Wichtige Teile

| Datei | Rolle |
|-------|-------|
| `app.py` | Der **Flask-Server**: Das Herz vom Cockpit. Er steuert Prüfungen, Chats und Daten. |
| `sse_server.py` | Der **Gedanken-Sender**: Ein System (SSE), das die Gedanken der KI live zum Browser schickt. |

## 🧪 Peak Demo: Ebene für Szenarien
Der Server hat eine **Ebene für Tests**. Er steuert die Krisen (Suez, Hamburg, etc.) im Speicher.
- **`_active_overrides`**: Speichert die Tests im Speicher des Servers.
- **Kombination von Daten**: Der Server kombiniert Fakten (SQL) mit den Tests für die Webseite oder die KI.

---

*Für die Anleitung gehen Sie zur Datei [5_vollstaendige_anleitung.md](../DE_documentation (in german)/5_vollstaendige_anleitung.md).*
