# Durchlauf — Resilienz.AI Peak Demo 🛡️✨

Resilienz.AI ist jetzt auf der höchsten Stufe für eine Demo. Diese Anleitung zeigt die neuen Funktionen und die Technik dahinter.

## 🌟 Neue "Wow-Effekt" Funktionen

### 1. **Weltkarte für Risiken**
Ein neuer Tab mit einer interaktiven Karte für die Lieferkette.
- **Visualrierung**: Karte zentriert auf Europa mit dunklem Design (**CartoDB Dark Matter**).
- **Daten**: Verbindet alle Lieferanten mit dem **Fabrik-Hub in Amberg** über Linien.
- **Intelligenz**: Orte blinken und ändern die Farbe (Rot / Gelb / Grün) bei einem Risiko.
- **Klick**: Klicke auf einen Ort für Infos über Vorrat und Verspätungen.

### 2. **Zentrum für Stress-Tests**
Im Tab "Risk Audit" kann man Krisen in der Welt simulieren.
- **Überblick**: Suezkanal-Sperrung, Hafen-Streik in Hamburg oder Energie-Krise.
- **Technik**: **In-memory-Tests**. Simulationen ändern keine Daten in der SQLite-Datenbank.
- **KI-Verbindung**: Das Programm schreibt automatisch eine Nachricht in **ChromaDB**. So kann die KI während der Prüfung über die neue Krise nachdenken.

### 3. **Gedanken-Spur der KI (Thought-Trace)**
Ein Monitor zeigt live, was die KI denkt.
- **Erfahrung**: Wenn eine Prüfung läuft, sieht man: "🧠 KI denkt nach...".
- **Detail**: Man sieht Schritte wie: "Suche: 12 Verspätungen gefunden", "Analyse: Bestätige Grund für Hafen-Streik" und "Schreiben: Bericht wird erstellt."
- **Technik**: Nutzt **Server-Sent Events (SSE)** für schnelles Streaming.

---

## 🛠️ Technische Architektur

### **Server-Ebene (`api/app.py`)**
- **Speicher**: Nutzt `_active_overrides` und `_thought_queues` für eine schnelle Demo.
- **Streaming**: Nutzt einen SSE-Server für die Gedanken der KI.
- **Karte**: Nutzt `data/map_data.py` für die Koordinaten der Lieferanten.

### **KI-Logik (`auditing.py`)**
- **Information**: Die KI teilt jeden Schritt bei der Untersuchung mit. Der Browser zeigt die Infos live.

### **Webseite (`dashboard/`)**
- **Design**: Modernes Design mit Glas-Effekt und Animationen (Puls-Effekt).
- **Karten-Integration**: Nutzt **Leaflet.js** mit dunklem Design.

---

## 🚀 Wie man eine Demo macht

1.  **Start**: Zeige die **Weltkarte** und die grünen Wege.
2.  **Krise**: Gehe zum Tab "Risk Audit" und wähle **"Suez-Sperrung"** aus. Klicke auf **Trigger**.
3.  **Beobachten**: Sieh das Abzeichen "Szenario Aktiv" und die neuen Verspätungen oben.
4.  **Verstehen**: Klicke auf **"Start Audit"**. Beobachte die **Gedanken-Spur**. Die KI findet jetzt die Suez-Krise und prüft betroffene Lieferanten in Asien.
5.  **Prüfen**: Lies den Bericht. Der Bericht zeigt jetzt die Probleme der Krise.
6.  **Ende**: Klicke auf **"Reset Data"**. Die Webseite ist wieder im sauberen Zustand.

---

## ✅ Aktueller Zustand des Projekts
Resilienz.AI ist ein moderner Prototyp. Er zeigt, wie eine Firma Risiken managen kann. Das Design ist premium und die KI ist transparent (man sieht alles). Das Projekt ist fertig für wichtige Präsentationen.
