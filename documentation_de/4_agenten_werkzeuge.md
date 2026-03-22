# Resilienz.AI — Werkzeuge des Agenten (Deep Dive) 🧰

Dieses Dokument erklärt die "Werkzeugkiste" für den **R_agent**. Jedes Werkzeug ist eine Python-Funktion. Damit arbeitet die KI mit echten Daten.

## 🎓 Die Strategie für Werkzeuge

Der Agent arbeitet in einer **Denk-Aktion-Schleife**:
1.  **Denken**: Der Agent sieht sich das Problem des Nutzers an.
2.  **Wählen**: Er nimmt das beste Werkzeug (Beispiel: `Lagerstatus`).
3.  **Aktion**: Die Python-Funktion arbeitet.
4.  **Beobachten**: Der Agent liest das Ergebnis und plant neu.

---

## 🧠 Transparenz live (Gedanken-Spur)
Ein wichtiges Ziel beim R_agent ist die **Gedanken-Spur (Thought-Trace)**.
- **Innerer Monolog**: Der Agent schickt seine Schritte zum Server. Er nutzt **Server-Sent Events (SSE)**.
- **Sehen**: Der Mitarbeiter sieht, *warum* der Agent Informationen von einem Lieferanten holt. Man sieht das vor dem finalen Bericht.

---

## 🗃️ Vorhandene Werkzeuge

### 1. `get_delayed_orders()`
- **Ziel**: Findet alle offenen Bestellungen mit einer Verspätung.
- **Nutzen**: Startet jede Prüfung, um Probleme zu finden.

### 2. `get_inventory_status(Teil_Nummer)`
- **Ziel**: Zeigt Menge im Lager, Vorrat in Tagen und täglichen Verbrauch.
- **Wichtig**: Hilft dem Agenten zu sehen, ob eine Verspätung ein Stopp für die Produktion ist.

### 3. `get_supplier_info(Lieferant_ID)`
- **Ziel**: Findet Zuverlässigkeit, Risikostufe und Kontakte für einen Notfall.
- **Wichtig**: Der Agent weiß jetzt, ob ein Lieferant vertrauenswürdig ist.

### 4. `search_global_events(Anfrage)`
- **Ziel**: Sucht in **ChromaDB** nach Nachrichten, Streiks oder Krisen in der Welt.
- **Vorteil**: Sucht nach dem **Sinn** (Beispiel: "Probleme beim Versand") und nicht nur nach Worten.

### 5. `calculate_risk_score(Bestell_ID)`
- **Ziel**: Berechnet eine Zahl (0-100) aus Verspätung, Vorrat und Wichtigkeit.
- **Wichtig**: Zeigt, welche Risiken zuerst im Bericht stehen müssen.

### 6. `get_alternative_supplier(Teil_Nummer)`
- **Ziel**: Findet den besten anderen Lieferanten für ein Teil.
- **Vorteil**: Der Agent schlägt einen "Plan B" vor, wenn ein normaler Weg blockiert ist.

### 7. `send_alert(an, Stufe, Text)`
- **Ziel**: Schickt einen Alarm oder eine E-Mail an den Mitarbeiter.
- **Aktion**: Das ist eine Aktion mit echten Folgen.

### 8. `generate_risk_report(IDs)`
- **Ziel**: Fasst alle Ergebnisse zusammen in einem Bericht (Markdown/PDF).
- **Resultat**: Diesen Bericht sieht man im Dashboard.

---

## 📊 Zusammenfassung der Werkzeuge

| Name des Werkzeugs | Quelle | Wichtige Information |
|--------------------|--------|----------------------|
| `get_delayed_orders` | SQL | Findet Bestellungen mit Problemen |
| `get_inventory_status` | SQL | Zeigt den Stopp für die Produktion |
| `search_global_events` | **Vector** | Findet den Grund für Probleme |
| `calculate_risk_score` | Logik | Zeigt die Wichtigkeit oben im Bericht |
| `get_alternative_supplier`| SQL | Findet die Lösung für den Notfall |

---

## 🎯 Beispiel für den Workflow

> **Nutzer**: "Gibt es ein Risiko bei PO-2024-001?"

1.  **Agent**: Nutzt `get_delayed_orders` → PO-2024-001 hat 7 Tage Verspätung.
2.  **Agent**: Nutzt `get_inventory_status` → Es gibt nur Vorrat für 2 Tage.
3.  **Agent**: Nutzt `search_global_events("Suez")` → Bestätigt den Grund.
4.  **Agent**: Nutzt `get_alternative_supplier` → Schlägt einen neuen Lieferanten vor.
5.  **Agent**: Schreibt die Antwort und schlägt den Plan vor.
