# Resilienz.AI — Daten-Architektur 📊

Resilienz.AI arbeitet mit einem Modell aus drei Welten. Das Projekt nutzt künstliche Daten für die Demo. Es gibt interne Daten, Daten von Lieferanten und Weltnachrichten.

---

## 🌎 Modell mit drei Welten

| Welt | Art der Daten | Speicher | Rolle |
|------|--------------|----------|-------|
| **Intern** | Bestellungen und Lager | SQLite | Was haben wir bestellt? Was ist im Lager? |
| **Lieferant** | Informationen über Verspätungen | SQLite | Was sagen die Lieferanten? |
| **Extern** | Nachrichten und Streiks | **ChromaDB** | Gibt es Probleme in der Welt? |

---

## 📂 Wichtige Daten-Teile

### 1. Bestellungen (`purchase_orders.csv`)
Das Herz des Systems. Es gibt Informationen wie ID, Lieferant und Wichtigkeit.
- **Warum Wichtigkeit?**: Wichtige Teile (Sensoren) lösen sofort einen Alarm aus. Einfache Teile (Schrauben) sind weniger wichtig.

### 2. Status vom Lieferanten (`supplier_status.csv`)
Nachrichten von den Lieferanten.
- **Wichtige Infos**: Tage der Verspätung, Grund und Ort.
- **Vorteil**: Die KI sieht sofort, wenn es Probleme gibt.

### 3. Lager (`inventory.csv`)
Wie viele Teile haben wir im Lager?
- **Tage im Lager**: Wie lange halten die Teile?
- **Die Regel**: Wenn die Verspätung länger dauert als der Vorrat im Lager, ist das ein großes Problem.

### 4. Lieferanten-Stamm (`suppliers.csv`)
Informationen über die Zuverlässigkeit der Lieferanten.
- **Punktzahl**: 0.0 bis 1.0 (wie oft ist der Lieferant pünktlich?).
- **Plan B**: Ein anderer Lieferant für einen Notfall.

### 5. Weltnachrichten (`global_events.csv`)
Gespichert in **ChromaDB (Vector DB)** für die Suche nach Sinn.
- **Ereignisse**: Streiks im Hafen oder Krisen bei der Energie.
- **Suche**: Die KI sucht nach Orten oder Themen (Beispiel: "Probleme in Deutschland").

---

## 🧪 Die dynamische Ebene für Szenarien (Neu)
Für die **Peak Demo** gibt es eine extra Ebene:
- **`_active_overrides`**: Ein Speicher im Server für simulierte Verspätungen.
- **`current_delay_days`**: Diese Zahl ändert sich bei einem Test-Szenario automatisch.
- **ChromaDB**: Bei einem Test kommen neue Nachrichten in die Datenbank. So findet die KI den Grund für ein Problem.

---

## 🛠️ Erstellung der Daten
Alle Daten werden mit einem Programm erstellt (`data/generate_data.py`). Das ist gut für:
1.  **Gleiche Daten**: Jede Demo nutzt die gleichen Informationen.
2.  **Sicherheit**: Es gibt keine echten Firmendaten.
3.  **Kontrolle**: Wir können schwere Probleme testen (Stress-Test).
