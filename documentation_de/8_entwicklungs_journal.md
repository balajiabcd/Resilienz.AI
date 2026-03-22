# Resilienz.AI — Entwicklungs-Journal: Der Weg von der Idee zur Peak Demo 📓🚀

Dieses Journal zeigt die Geschichte von Resilienz.AI. Jede Entscheidung und jeder Meilenstein steht hier.

---

## 🛠️ Schritt 0: Die Planung (20.03.2026)
**Ziel**: Eine KI für deutsche Firmen (KMU) planen. Die KI findet Probleme in der Lieferkette.

### Wichtige Entscheidungen:
- **Namen**: Die helfende KI ist **Ramya**; die Haupt-KI im Projekt ist **R_agent**.
- **Hybride DB**: **SQLite** für Zahlen (Bestellungen) + **ChromaDB** für Texte (Nachrichten).
- **Architektur**: Plan mit 4 Schichten (Daten → Gehirn → Aktion → Dashboard).

---

## 🏗️ Schritt 1: Das Fundament & Simulation
**Ziel**: Ein Skelett für das Projekt bauen und künstliche Daten erstellen.
- **Erfolg**: Bau von `data/generate_data.py`. Erstellung von 5 CSV-Dateien für SQLite und ChromaDB.
- **Test-Fall**: Wir haben **PO-2024-001** gebaut. 8 Tage Verspätung und nur 2,5 Tage Vorrat im Lager. Das ist unser Beispiel für ein großes Problem.

---

## 🧰 Schritt 2: Die "Hände" (Werkzeuge)
**Ziel**: Funktionen für die KI bauen (Python-Tools). Damit kann sie alles sehen und berechnen.
- **Erfolg**: Bau von 8 Werkzeugen, zum Beispiel `Lagerstatus`, `Sinn-Suche` und `Risiko-Zahl`.
- **Lernen**: Wir haben gelernt, dass eine KI Tabellen (Markdown) besser versteht als Code (JSON).
- **Logik**: Die Risiko-Zahl berechnet Python (0-100). Die KI rät nicht, sondern nutzt feste Regeln.

---

## 🧠 Schritt 3: Das Gehirn der KI (Multi-LLM)
**Ziel**: Gemini verbinden und einen Plan B bauen, wenn die KI nicht antwortet.
- **Erfolg**: Bau von **LLMSwitch**. Wenn Gemini Flash nicht antwortet, nutzt das System automatisch mehr als 20 andere KIs (über OpenRouter).
- **Resultat**: Der Agent ist jetzt sicher und arbeitet immer bis zum Ende.

---

## 📄 Schritt 4: Verbindung zur Welt (Alarme)
**Ziel**: Der Agent soll im echten Leben Aktionen machen.
- **Erfolg**: Integration von `notifier.py`. Das Programm schickt jetzt E-Mails und erstellt PDF-Berichte mit Logo.
- **Logik**: Der Agent schickt nur dann Alarme, wenn das Risiko höher als 70 Punkte ist.

---

## 🖥️ Schritt 5: Das Dashboard (Webseite)
**Ziel**: Ein modernes Cockpit für die Mitarbeiter bauen.
- **Erfolg**: Bau eines Servers (Flask) und einer Webseite mit modernem Glas-Effekt.
- **Funktion**: Live-Zahlen, Live-Anzeige der Berichte und ein Chat mit dem Agenten.
- **Status**: Das Projekt ist jetzt ein fertiger Prototyp.

---

## 🌟 Schritt 6: Die Peak Demo Erweiterungen (Heute)
**Ziel**: Die höchste Stufe für die Demo bauen (Wow-Effekt).
- **Erfolg 1 (Die Karte)**: Bau der **Weltkarte** mit Leaflet.js. Man sieht blinkende Punkte bei Risiken auf dem Weg zur Fabrik in Amberg.
- **Erfolg 2 (Das Labor)**: Bau des **Szenario-Centers**. Man kann Krisen (Suez, Streik) als **Simulation im Speicher** testen. Keine echten Daten werden geändert.
- **Erfolg 3 (Die Spur)**: Bau der **Gedanken-Spur**. Man sieht die Gedanken der KI live über **SSE (Server-Sent Events)** im Browser.

---

## 🏁 Finaler Zustand des Projekts
Resilienz.AI ist jetzt ein moderner und transparenter KI-Agent. Alles ist dokumentiert und getestet. Das Projekt ist fertig für jede Präsentation in der deutschen Industrie.
