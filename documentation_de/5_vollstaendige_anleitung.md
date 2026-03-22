# Resilienz.AI — Komplette Übersicht & Anleitung 🛡️

**Resilienz.AI** ist ein Cockpit für den Einkauf in deutschen Firmen (KMU). Es findet Probleme in der Lieferkette und hilft bei der Lösung. Die KI arbeitet selbstständig.

---

## 🚀 1. Was kann das System?

### **Überwachung von Risiken**
- **Suchen**: Das Programm sieht in **SQLite** (Bestellungen) und **ChromaDB** (Weltnachrichten) nach Problemen.
- **Denken**: Es nutzt Python für Daten und eine KI (Gemini) für die Analyse.
- **Finden**: Es zeigt sofort, wenn Teile fehlen oder Verspätungen drohen.

### **Der KI-Agent (R_agent)**
- **Denk-Prozess**: Zeigt dem Nutzer jeden Schritt bei der Arbeit (**Thought-Trace**).
- **Flexibel**: Wenn eine KI nicht antwortet, nutzt das System automatisch eine andere.
- **Ausgabe**: Schreibt Berichte in Markdown und PDF für den Chef.

---

## 🎨 2. Das Dashboard (Übersicht)

### **Wichtige Zahlen (Live)**
- **Aktive Lieferanten**: Wie viele Firmen liefern aktuell?
- **Bestellungen unterwegs**: Wie viele Teile kommen aktuell?
- **Bestellungen mit Verspätung**: **(Wichtig)** Wie viele Teile kommen zu spät?
- **Katalog**: Wie viele verschiedene Teile managt das System?

### **Globale Weltkarte (Neu)**
- **Ort**: Zeigt alle Lieferanten auf einer Karte.
- **Fabrik Amberg**: Der Ort der Fabrik ist das Zentrum.
- **Linien**: Verbinden Lieferanten mit der Fabrik. Die Farbe (Rot/Gelb/Grün) zeigt das Risiko.
- **Animation**: Wenn ein Risiko hoch ist, blinkt der Ort auf der Karte.

---

## 🌋 3. Stress-Test Szenario Center

Hier können Mitarbeiter Krisen testen. Das System ändert keine echten Daten in der Datenbank.

| Szenario | Effekt | Regionen |
|----------|--------|-----------|
| **Suez Kanal** | +14 Tage Verspätung | Japan, China, S. Korea |
| **Streik (Hafen)** | +7 Tage Verspätung | Deutschland (Hamburg) |
| **Energie Krise** | +4 Tage Verspätung | Deutschland (Ganzes Land) |

- **Weg**: Die Tests sind nur im Speicher des Servers (in-memory).
- **Reset**: Ein Klick und das Dashboard zeigt wieder normale Daten.

---

## 💬 4. Zusammenarbeit mit der KI

### **Wissenschaftliche Prüfung (Audit)**
- **Weg**: Ein Klick startet die Suche. Die KI prüft die gesamte Lieferkette.
- **Transparenz**: Man sieht den Live-Log: *Suche... Analyse... Bericht geschrieben.*
- **Ergebnis**: Ein Bericht mit einer Tabelle aller kritischen Teile und Lösungen.

### **Chat mit R_agent**
- **Fragen**: Man kann im Chat fragen: *"Ist Bestellung PO-123 sicher?"* oder *"Haben wir genug Vorrat für Sensoren?"*
- **Schnell**: Der Agent kennt das Lager und die Nachrichten und antwortet in 2-5 Sekunden.

---

## 🛠️ 5. Anleitung für die Nutzung (Start)

### **A. Starten**
1.  **Server starten**: Nutze `python api/app.py`.
2.  **Dashboard öffnen**: Öffne die Datei `dashboard/index.html` im Browser.
3.  **Status prüfen**: Das grüne Licht an der Sidebar muss blinken.

### **B. Eine Prüfung machen**
1.  Gehe zum Tab **Risk Audit**.
2.  Klicke auf **🚀 Start Audit**.
3.  Beobachte die **Gedanken-Spur (Thought-Trace)**.
4.  Lies den Bericht, wenn "Reasoning complete" da steht.

### **C. Einen Stress-Test machen**
1.  Wähle im Tab **Audit** ein Szenario (Beispiel: *Streik — Hamburg*).
2.  Klicke auf **⚡ Trigger**.
3.  Gehe zum Tab **Global Map**. Die Wege bei Deutschland sind jetzt Rot.
4.  Prüfe die Zahlen oben (Verspätungen steigen).

### **D. Chat**
1.  Gehe zum Tab **💬 Chat**.
2.  Schreibe deine Frage unten in die Zeile.
3.  Die KI liest die Daten und antwortet.

---

## ✅ Technik Zusammenfassung
-   **Webseite**: HTML/CSS/JS (Glasmorphism Design) + Leaflet.js.
-   **Server**: Flask (Python) mit SSE für Live-Updates.
-   **Daten**: SQLite (Zahlen/ID) + ChromaDB (Texte/Nachrichten).
-   **KI**: Gemini Flash (Haupt-KI) + OpenRouter Fallback.
