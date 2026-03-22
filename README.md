# Resilienz.AI — Plattform für die Sicherheit der Lieferkette 🛡️🚀

**Resilienz.AI** ist ein Cockpit für den Einkauf in deutschen Firmen (KMU). Es findet Probleme in der Lieferkette und prüft Krisen mit einer "Denk-Aktion-Schleife". Es zeigt dem Nutzer live, wie der Agent denkt.

## 🌟 Peak Demo Funktionen (Neu am 22.03.2026)
- 🌍 **Sicherheits-Weltkarte**: Eine interaktive Karte mit Leaflet.js. Man sieht die Wege und Orte mit Risiken.
- 🌋 **Stress-Test Center**: Sichere Simulationen von Krisen im Speicher des Servers (Suez-Kanal, Streik).
- 🧠 **KI-Gedanken-Spur**: Live-Anzeige der Gedanken der KI über Server-Sent Events (SSE).

---

## 📂 Struktur des Projekts

| Ordner | Zweck |
|--------|-------|
| [**documentation/**](./documentation/1_project_plan.md) | **Haupt-Archiv**: Die Geschichte des Projekts, die Architektur und die Anleitung. |
| [agent/](./agent/README.md) | Das Gehirn der KI (Multi-LLM) und seine "Hände" (Python Werkzeuge). |
| [api/](./api/README.md) | Der Flask-Server mit Live-Gedanken und der Logik für Krisen-Tests. |
| [dashboard/](./dashboard/README.md) | Die Webseite: Ein modernes Cockpit für den Nutzer. |
| [data/](./data/README.md) | Künstliche Daten (SQLite + ChromaDB) und die Ebene für Tests. |
| [alerts/](./alerts/README.md) | Das System für Nachrichten: E-Mails und PDF-Berichte. |

---

## 🚀 Schneller Start (Demo-Modus)

```bash
# 1. Installiere die Programme
pip install -r requirements.txt

# 2. Starte den Server (Port 5000)
python api/app.py

# 3. Öffne das Cockpit
# Öffne dashboard/index.html in einem Browser.
```

## 🧠 Technische Vision
Resilienz.AI nutzt zwei Datenbanken (**SQLite + ChromaDB**) und eine Architektur mit mehreren KIs. Das System zeigt dem Menschen alle Schritte der KI. Kritische Daten sind keine "Black Box" mehr.

---

*Für technische Details gehen Sie in den Ordner [documentation/](./documentation/1_project_plan.md).*
