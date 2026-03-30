# Resilienz.AI — Autonome Lieferketten-Resilienzplattform

> **Produktionsinspirierte KI-Agentenarchitektur für Lieferketten-Risikomanagement**

---

## 🚀 Schnelle Demo (30 Sekunden)

```bash
# 1. Backend starten
python api/app.py

# 2. Dashboard öffnen
# → dashboard/index.html im Browser öffnen

# 3. "🚀 Audit starten" klicken
# 4. KI-Gedanken-Stream in Echtzeit beobachten
```

👉 **Demo-Video**: [my youtube demo link]

---

## Architektur TL;DR

- **Agenten-Schleife**: Denken → Handeln → Beobachten → Reflektieren
- **Deterministische Schicht**: Risikoberechnung, Verzögerungsberechnung, Bestandsschwellenwerte
- **LLM-Schicht**: Begründung, Priorisierungsverfeinerung, Berichterstellung
- **Werkzeug-Schicht**: SQLite + Vector DB + E-Mail/PDF-Warnungen
- **Resilienz**: Multi-Modell-Failover über OpenRouter (20+ Modelle)

---

## 1. Projektübersicht

**Resilienz.AI** ist ein autonomes, KI-gesteuertes Beschaffungs-Cockpit für deutsche Fertigungs-KMU. Es verwandelt reaktives Lieferkettenmanagement in einen proaktiven, intelligenten Betrieb durch eine autonome „Think-Act-Loop"-Agentenarchitektur.

### Das Problem

Kleine und mittlere Fertigungsunternehmen in Deutschland haben ein großes Problem: **Lieferkettenunterbrechungen können Produktionslinien stoppen**. Aber sie haben nicht genug Geld für eigene Risiko-Überwachungsteams. Wenn man reagiert, findet man Probleme erst, wenn sie Lieferungen schon beeinflusst haben.

### Die Lösung

Resilienz.AI nutzt einen spezialisierten KI-Agenten. Dieser Agent überwacht ständig Bestellungen, Lagerbestände, Lieferantenleistung und globale Ereignisse. So kann er Risiken erkennen, analysieren und vermeiden, bevor sie die Produktion stoppen.

### Was ist anders?

| Traditioneller Weg          | Resilienz.AI                          |
| --------------------------- | ------------------------------------- |
| Manuelle Überprüfungen    | Kontinuierliche autonome Überwachung |
| Black-Box KI-Entscheidungen | Volle Transparenz durch Thought-Trace |
| Reaktives Problemlösen     | Proaktive Risikoerkennung             |
| Abhängigkeit von einem LLM | Multi-Modell-Architektur              |
| Eine Datenquelle            | Hybrid SQLite + Vector DB             |

---

## 2. Warum Agentenbasiert statt Dashboard-Analyse?

Traditionelle Dashboards zeigen Daten. Resilienz.AI handelt darauf.

| Dashboard-Analyse                  | Resilienz.AI Agent                  |
| ---------------------------------- | ----------------------------------- |
| Zeigt rohe Daten                   | Erkennt Risiken automatisch         |
| Braucht menschliche Interpretation | Untersucht Ursachen automatisch     |
| Statische Filter und Warnungen     | Empfiehlt konkrete Maßnahmen       |
| Passive Anzeige                    | Führt Warnungen aus (Risiko ≥ 70) |

**Der Unterschied**: Passive Analytik → Aktives Entscheidungsunterstützungssystem

Der Agent zeigt nicht nur Informationen. Er:

1. Überwacht den Lieferkettenzustand ständig
2. Untersucht Anomalien selbstständig
3. Berechnet Risiken mit deterministischer + LLM-Begründung
4. Löst Eskalationen aus, ohne dass ein Mensch eingreifen muss

---

## 3. Autonomie-Modell

| Aspekt                                | Implementierung                                                     |
| ------------------------------------- | ------------------------------------------------------------------- |
| **Auslöser-Modus**             | Manuell (über UI) + Bereit für geplante Ausführung (cron-bereit) |
| **Entscheidungsfindung**        | Vollautomatische Risikobewertung                                    |
| **Aktionen**                    | Warnungen + Empfehlungen (automatische Eskalation bei Risiko ≥ 70) |
| **Menschliche Überschreibung** | Immer möglich durch Thought-Trace-Sichtbarkeit                     |

---

## 4. Wichtige Funktionen

### Intelligenz-Schicht

| Funktion                             | Beschreibung                                                                                   |
| ------------------------------------ | ---------------------------------------------------------------------------------------------- |
| **Echtzeit-Risikoerkennung**   | Überwacht 50+ Bestellungen mit Lieferantenstatus, Lagerpuffern und globalen Störungssignalen |
| **Think-Act-Loop Architektur** | Autonomer Agent durchläuft Denken → Planen → Handeln → Beobachten → Reflektieren          |
| **Szenario-Simulation**        | Risikofreie Speichertests für geopolitische Krisen, Hafenarbeiterstreiks und Energiekrisen    |

### Transparenz-Schicht

| Funktion                       | Beschreibung                                                                             |
| ------------------------------ | ---------------------------------------------------------------------------------------- |
| **KI Thought-Trace**     | Echtzeit-Streaming der internen Überlegungen des Agenten über Server-Sent Events (SSE) |
| **Erklärbare Ausgaben** | Jedes Risikoergebnis zeigt Datenquellen, Bewertungsfaktoren und Konfidenzniveau          |
| **Audit-Trail**          | Vollständige Protokollierung aller Agentenentscheidungen                                |

### Visualisierungs-Schicht

| Funktion                      | Beschreibung                                                                      |
| ----------------------------- | --------------------------------------------------------------------------------- |
| **Globale Risikokarte** | Interaktive Leaflet.js-Karte zeigt Lieferantenstandorte, Routen und Risikogebiete |
| **Routenverfolgung**    | Visuelle Verbindung vom Werk zu Lieferanten mit Verzögerungsanzeigen             |
| **Szenario-Dashboards** | Echtzeit-Dashboard-Updates bei Szenarioaktivierung                                |

---

## 5. Systemarchitektur

![System Architecture](images/architecture.png)

### Datenfluss-Architektur

![Data Flow](images/data-flow.png)

### Komponenten-Verantwortlichkeiten

| Komponente                | Verantwortung                                                        | Technologie             |
| ------------------------- | -------------------------------------------------------------------- | ----------------------- |
| **RAgent (Gehirn)** | Koordiniert Denkschleife, Werkzeugauswahl und Antwortzusammenfassung | Python 3.11+            |
| **LLMSwitch**       | Modell-agnostisches LLM-Routing mit automatischem Failover           | OpenRouter SDK          |
| **Werkzeugschicht** | Python-Funktionen für Datenabruf und Aktionen                       | SQLite, ChromaDB        |
| **Audit-Modul**     | Hybrid-Logik: deterministisches Python + LLM-Phasen                  | Python + LLM            |
| **API-Server**      | REST-Endpunkte, SSE-Streaming, Szenarioverwaltung                    | Flask + Flask-CORS      |
| **Dashboard**       | Glassmorphism UI, interaktive Karte, Thought-Trace-Anzeige           | Vanilla JS + Leaflet.js |
| **Datenschicht**    | Strukturierte Daten (SQLite) + Semantischer Kontext (Vector DB)      | SQLite, ChromaDB        |

---

## 6. Agentendesign

### Think-Act-Loop Architektur

Resilienz.AI nutzt einen verbesserten autonomen Agentenloop. Er basiert auf ReAct-Mustern (Reason + Act) mit zusätzlichen Reflexionszyklen:

![Agent Flow](images/agent-flow.png)

### Deterministisch vs LLM Aufteilung

| Was                           | Wer macht es                     | Warum                                            |
| ----------------------------- | -------------------------------- | ------------------------------------------------ |
| Risikoberechnung (0-100)      | **Deterministisch** Python | Mathematisch präzise, kein Halluzinationsrisiko |
| Verzögerungsberechnung       | **Deterministisch** Python | Exakte Zahlen erforderlich                       |
| Bestandsschwellenwertprüfung | **Deterministisch** Python | Boolesche Logik, keine Mehrdeutigkeit            |
| Risikoerklärung              | **LLM**                    | Natürliche Sprachausgabe                        |
| Priorisierungsverfeinerung    | **LLM**                    | Kontextbewusste Sortierung                       |
| Berichterstellung             | **LLM**                    | Professionelles Format                           |
| Globale Ereignisrelevanz      | **LLM + Vector DB**        | Semantisches Verständnis                        |

### Prompt-Engineering-Strategie

Der Agent nutzt eine **optimierte Prompt-Architektur** mit effizientem Tokenmanagement:

![Prompt Structure](images/prompt-structure.png)

### Entscheidungsstrategie

1. **Erkennung**: Python holt alle verzögerten Bestellungen
2. **Priorisierung**: LLM filtert die 5 wichtigsten kritischen Bestellungen
3. **Untersuchung**: Jede Bestellung bekommt eine individuelle LLM-Analyse
4. **Synthese**: Finales LLM erstellt eine Zusammenfassung
5. **Aktion**: Automatische Eskalation bei Risikowert ≥ 70

---

## 7. Werkzeuge und Integrationen

### Datenquellen-Werkzeuge

| Werkzeug                   | Datenquelle | Anwendungsfall                         |
| -------------------------- | ----------- | -------------------------------------- |
| `get_delayed_orders()`   | SQLite      | Findet Bestellungen mit Verzögerungen |
| `get_inventory_status()` | SQLite      | Prüft Lagerbestand und Reichweite     |
| `get_supplier_info()`    | SQLite      | Zeigt Lieferantenzuverlässigkeit      |
| `search_global_events()` | ChromaDB    | Semantische Suche nach Störungen      |

### Aktions-Werkzeuge

| Werkzeug                       | Ziel          | Anwendungsfall                            |
| ------------------------------ | ------------- | ----------------------------------------- |
| `calculate_risk_score()`     | Interne Logik | Deterministische Risikoberechnung (0-100) |
| `get_alternative_supplier()` | SQLite        | Findet Ersatzlieferanten                  |
| `send_risk_alert()`          | E-Mail + PDF  | Automatische Warnung mit Maßnahmenplan   |

### Externe Integrationen

| Integration              | Technologie        | Zweck                              |
| ------------------------ | ------------------ | ---------------------------------- |
| **Karten**         | Leaflet.js + CARTO | Globale Lieferantenvisualisierung  |
| **LLM Gateway**    | OpenRouter API     | Multi-Modell-Inferenz mit Failover |
| **E-Mail**         | SMTP (Gmail)       | Warnungsbenachrichtigungen         |
| **PDF-Erstellung** | fpdf2              | Risikobericht-Erstellung           |

---

## 8. Stresstest-Simulations-Engine

Dies ist eine besondere Funktion. Sie ermöglicht **risikofreie Entscheidungsunterstützung** durch Szenarioplanung.

### Verfügbare Szenarien

| Szenario                                | Beschreibung                                    | Betroffene Regionen               | Verzögerung |
| --------------------------------------- | ----------------------------------------------- | --------------------------------- | ------------ |
| **Suez-Blockade**                 | Simulierte Krisensituation im Roten Meer        | Japan, China, Südkorea           | +10-14 Tage  |
| **Hamburger Hafenarbeiterstreik** | Simulierter Streik am größten deutschen Hafen | Deutschland, Niederlande, Belgien | +7 Tage      |
| **Energiekrise**                  | Simulierter nationwide Energiemangel            | Deutschland                       | +4 Tage      |

### Wie Simulationen funktionieren

![Simulation Flow](images/simulation.png)

### Warum ist das wichtig?

- **Kein echtes Risiko**: Alle Änderungen sind nur im Speicher. Die echten Daten bleiben unberührt.
- **"Was-wäre-wenn"-Analyse**: Man kann Strategien testen, ohne die Lieferkette zu gefährden.
- **Sofortiges Feedback**: Das Dashboard zeigt die Auswirkungen sofort.
- **Deterministisch + Semantisch**: Kombiniert Datenbankänderungen mit durchsuchbaren Ereignissen.

---

## 9. Erklärbarkeit und Thought-Trace

### Was wird gezeigt?

Jeder Denkzyklus des Agenten zeigt:

- **Schrittname**: Erkennung, Aggregation, Untersuchung, Synthese, Fertig
- **Zeitstempel**: Wann jeder Schritt abgeschlossen wurde
- **Detail**: Konkrete Ergebnisse (z.B. „5 verzögerte Bestellungen gefunden")
- **Werkzeugaufrufe**: Welche Werkzeuge mit welchen Parametern aufgerufen wurden

### Technische Umsetzung

```javascript
// Frontend SSE Verbindung
const eventSource = new EventSource('/api/stream/thoughts');
eventSource.onmessage = (e) => {
    const { step, detail } = JSON.parse(e.data);
    addThoughtItem(step, detail);  // Live UI Update
};
```

### Warum ist das wichtig?

1. **Vertrauen aufbauen**: Benutzer sehen, *warum* der Agent eine Empfehlung gibt.
2. **Nachvollziehbarkeit**: Komplette Spur für Compliance-Anforderungen.
3. **Fehlersuche**: Leichtes Erkennen von Denkfehlern.
4. **Mensch-in-der-Schleife**: Operatoren können bei jedem Schritt eingreifen.

---

## 10. Design-Abwägungen

| Entscheidung                                | Gewählt                      | Begründung                                                                |
| ------------------------------------------- | ----------------------------- | -------------------------------------------------------------------------- |
| **SQLite vs PostgreSQL**              | SQLite                        | Einfachheit und Portabilität für Demo; kein externer DB-Server nötig    |
| **SSE vs WebSockets**                 | SSE                           | Einfachheit und unidirektionales Streaming; ausreichend für Thought-Trace |
| **Multi-Modell vs Einzelmodell**      | Multi-Modell über OpenRouter | Resilienz über Konsistenz; Failover verhindert Deadlocks                  |
| **Python LLM-Werkzeuge vs LangChain** | Eigene Implementierung        | Volle Kontrolle, leichterer Fußabdruck, bessere Lernerfahrung             |
| **In-Memory-Szenarien vs persistent** | In-Memory Overrides           | Risikofreies Testen ohne Berührung der Produktionsdaten                   |

---

## 11. Mock-Daten-Strategie

Die Demo verwendet **deterministisch generierte Daten**, um Reproduzierbarkeit zu gewährleisten:

- **20 Lieferanten** aus Deutschland, Europa, Asien und Nordamerika
- **50 Bestellungen** mit realistischen Teilenummern und Mengen
- **15 globale Ereignisse** aus Politik, Wetter und Arbeitsmarkt
- **Seed-basierte Generierung** (`DATA_SEED = 42`) sichert gleiche Daten bei jedem Lauf

**Produktionsweg**: `generate_data.py` durch echte ERP/API-Integrationen ersetzen. Die Werkzeugschicht bleibt unverändert.

---

## 12. Technologie-Stack

### Backend

| Komponente                         | Technologie   | Version |
| ---------------------------------- | ------------- | ------- |
| **Laufzeit**                 | Python        | 3.11+   |
| **Web-Framework**            | Flask         | 3.0+    |
| **Datenbank (Strukturiert)** | SQLite        | 3.x     |
| **Datenbank (Vektor)**       | ChromaDB      | 0.4+    |
| **LLM Gateway**              | OpenRouter    | API     |
| **PDF-Erstellung**           | fpdf2         | 2.7+    |
| **Konfiguration**            | python-dotenv | 1.0+    |

### Frontend

| Komponente              | Technologie                 | Version |
| ----------------------- | --------------------------- | ------- |
| **UI-Framework**  | Vanilla JS                  | ES6+    |
| **Karten**        | Leaflet.js                  | 1.9+    |
| **Kartenkacheln** | CARTO Dark Matter           | -       |
| **Styling**       | Eigenes CSS (Glassmorphism) | -       |
| **Streaming**     | Server-Sent Events          | Nativ   |

### KI/ML

| Komponente                  | Technologie                              | Hinweise               |
| --------------------------- | ---------------------------------------- | ---------------------- |
| **Primäre Modelle**  | OpenRouter Aggregiert                    | 20+ kostenlose Modelle |
| **Modell-Switch**     | Eigenes LLMSwitch                        | Auto-Failover          |
| **Benchmark-Modelle** | Gemini 2.0 Flash, Llama 3.3, DeepSeek R1 | getestet               |

---

## 13. Wichtige API-Endpunkte

| Methode  | Endpunkt                   | Beschreibung                            |
| -------- | -------------------------- | --------------------------------------- |
| `POST` | `/api/agent/audit`       | Autonomes Risikoaudit auslösen         |
| `POST` | `/api/agent/chat`        | Agent mit natürlicher Sprache abfragen |
| `GET`  | `/api/stream/thoughts`   | SSE-Stream der Agentenbegründung       |
| `GET`  | `/api/map/data`          | Geografische Lieferantendaten           |
| `POST` | `/api/scenario/trigger`  | Stresstest-Szenario aktivieren          |
| `POST` | `/api/scenario/reset`    | Szenario zurücksetzen                  |
| `GET`  | `/api/dashboard/summary` | Zusammenfassungsmetriken                |
| `GET`  | `/api/orders/delayed`    | Liste verzögerter Bestellungen         |
| `GET`  | `/api/inventory`         | Aktuelle Lagerbestände                 |

---

## 14. Einrichtung und Installation

### Voraussetzungen

- Python 3.11+
- Moderner Webbrowser (Chrome, Firefox, Edge)
- OpenRouter API-Schlüssel (kostenloser Tier verfügbar)

### Installation

```bash
# Repository klonen
git clone https://github.com/yourusername/Resilienz.AI.git
cd Resilienz.AI

# Virtuelle Umgebung erstellen
python -m venv .venv
source .venv/bin/activate  # Auf Windows: .venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Umgebung konfigurieren
cp .env.example .env
# .env bearbeiten und OPENROUTER_API_KEY hinzufügen
```

### Anwendung starten

```bash
# Terminal 1: Backend starten (Port 5000)
python api/app.py

# Terminal 2: Dashboard öffnen
# dashboard/index.html im Browser öffnen
```

### Umgebungsvariablen

| Variable               | Erforderlich | Beschreibung                                         |
| ---------------------- | ------------ | ---------------------------------------------------- |
| `OPENROUTER_API_KEY` | Ja           | API-Schlüssel von openrouter.ai                     |
| `ALERT_EMAIL_FROM`   | Nein         | Absender-E-Mail (Standard: agent@resilienz.ai)       |
| `ALERT_EMAIL_TO`     | Nein         | Empfänger-E-Mail (Standard: procurement@company.de) |
| `SMTP_PASSWORD`      | Nein         | App-Passwort für Gmail SMTP                         |

---

## 15. Benutzungsanleitung

### Risikoaudit starten

1. Dashboard öffnen (`dashboard/index.html`)
2. **„🚀 Audit starten"** im Risikoaudit-Panel klicken
3. Den **KI Thought-Trace** in Echtzeit beobachten
4. Den generierten **Executive Bericht** lesen

### Mit dem Agenten sprechen

1. Zum **Chat**-Tab wechseln
2. Eine Frage eingeben (z.B. „Welche Lieferanten haben Zuverlässigkeit unter 85%?")
3. Natürliche Sprachantwort mit Datenangaben erhalten

### Stresstest durchführen

1. Ein Szenario aus dem Dropdown auswählen (z.B. „Suez-Kanal-Blockade")
2. **„⚡ Auslösen"** klicken
3. Beobachten:

   - Kartenmarkierungen werden orange/rot
   - Betroffene Lieferanten zeigen Verzögerungen
   - Dashboard-Metriken aktualisieren
4. **„🔄 Zurücksetzen"** klicken, um zum Ausgangszustand zurückzukehren

---

## 16. Beispielausgabe

### Beispiel-Risikobericht

```markdown
# EXECUTIVE RISIKOZUSAMMENFASSUNG — 27. März 2026

## Identifizierte kritische Bestellungen

| Bestell-Nr. | Teil | Lieferant | Risikowert | Status |
|-------|------|----------|------------|--------|
| PO-2024-012 | Sensor-X1 | TechParts GmbH | 78 | 🔴 KRITISCH |
| PO-2024-008 | Motor-K4 | Motoren AG | 65 | 🟠 HOCH |
| PO-2024-015 | Lager-7 | Lagerwerk SE | 52 | 🟡 MITTEL |

## Zusammenfassung

Die Lieferkette zeigt **erhöhtes Risiko** wegen:
- 3 Bestellungen mit Verzögerungen über dem Lagerpuffer
- 1 Lieferant (TechParts GmbH) mit Zuverlässigkeit unter 80%
- Aktuelle globale Ereignisse in asiatischen Schifffahrtswegen

## Empfohlene Maßnahmen

1. **Sofort**: TechParts GmbH wegen Lieferbestätigung kontaktieren
2. **Kurzfristig**: Ersatzlieferant für Sensor-X1 aktivieren
3. **Überwachung**: Tägliche Auditzyklen fortsetzen
```

### Thought-Trace Beispiel

```
┌────────────────────────────────────────────────────────────┐
│  🧠 KI denkt nach...                                        │
├────────────────────────────────────────────────────────────┤
│  10:42:15  ── Erkennung ── 5 verzögerte Bestellungen gefunden│
│  10:42:16  ── Aggregation ── Daten für 5 Ziele sammeln      │
│  10:42:17  ── Untersuchung ── Analysiere (1/3) — PO-2024-012│
│  10:42:18  ── Untersuchung ── Analysiere (2/3) — PO-2024-008│
│  10:42:19  ── Untersuchung ── Analysiere (3/3) — PO-2024-015│
│  10:42:20  ── Synthese ── Finalen Bericht erstellen         │
│  10:42:21  ── ✅ Fertig ── 3 Risiken identifiziert        │
└────────────────────────────────────────────────────────────┘
```

---

## 17. Leistung und Bewertung

### Systemmetriken

| Metrik                      | Wert           | Hinweise                      |
| --------------------------- | -------------- | ----------------------------- |
| **Audit-Abschluss**   | ~8-15 Sekunden | Abhängig von LLM-Antwortzeit |
| **SSE-Latenz**        | <100ms         | Browser-natives Streaming     |
| **Datenbankabfragen** | 5-12 pro Audit | Nur deterministisches Python  |

### Genauigkeitsmerkmale

Die Hybrid-Architektur sorgt für:

- **Deterministische Berechnung**: Risikowerte werden mathematisch berechnet (keine LLM-Halluzination bei Zahlen)
- **Semantische Suche**: ChromaDB liefert relevanten Kontext ohne Stichwortabhängigkeit
- **Failover-Zuverlässigkeit**: 20+ Modelle über OpenRouter verfügbar

### Bekannte Fehlerfälle

| Fehler                            | Ursache                                         | Gegenmaßnahme                                                    |
| --------------------------------- | ----------------------------------------------- | ----------------------------------------------------------------- |
| Falsche Priorisierung             | Fehlende Lieferantendaten im Kontext            | Kontextfenster vergrößern oder Fallback-Datenquelle hinzufügen |
| LLM-Überverallgemeinerung        | Modell generiert plausible aber falsche Ursache | Deterministische Bewertungsschicht als Grundlage                  |
| Szenario-Injektion fehlgeschlagen | ChromaDB nicht verfügbar                       | Anmutende Degradation; Szenario gilt trotzdem für SQLite         |

### Testfall

> **Szenario**: TechParts GmbH Lieferung um 12 Tage verzögert
>
> - Lagerpuffer: 8 Tage
> - Risikoberechnung: 12 ≥ 8 → Wert +50
> - Kritikalität: HOCH → Wert +25
> - Ergebnis: Wert 75 → Automatische Eskalation ausgelöst

---

## 18. Einschränkungen

| Einschränkung                       | Auswirkung                                        | Gegenmaßnahme                                   |
| ------------------------------------ | ------------------------------------------------- | ------------------------------------------------ |
| **Externe Datenqualität**     | Globale Ereignisdatenbank ist simuliert           | Echtzeit-API-Integration geplant                 |
| **LLM Halluzinationsrisiko**   | Agent kann Kontext falsch verstehen               | Deterministische Bewertungsschicht als Grundlage |
| **Simulationsvereinfachungen** | Szenarien nutzen feste Verzögerungsmodifikatoren | Konfigurierbare Szenarioparameter                |
| **Kontextfenster-Grenzen**     | Kleinere Modelle haben begrenzten Kontext         | Kontextbewusste Kürzung und Hybrid-Architektur  |
| **Rate-Limits**                | Kostenloser Tier hat Nutzungsquoten               | Automatisches Modell-Failover                    |

---

## 19. Zukünftige Arbeit

### Kurzfristig (Q2 2026)

- [ ] Echtzeit-Nachrichten-API-Integration (GDELT, NewsAPI)
- [ ] Multi-Agenten-Koordination (separate Agenten für Erkennung → Maßnahmen)
- [ ] Prädiktive Risikobewertung (ML-Modell für Lieferzeitvorhersage)

### Mittelfristig (Q3-Q4 2026)

- [ ] Lieferanten-Kollaborationsportal
- [ ] ERP-Integration (SAP, Microsoft Dynamics)
- [ ] Automatisierte Nachbestellungsempfehlungen
- [ ] Mehrsprachige Unterstützung

### Langfristig (2027+)

- [ ] Blockchain-basierte Lieferantenverifizierung
- [ ] Föderiertes Lernen für unternehmensübergreifende Erkenntnisse
- [ ] Sprachassistent-Integration

---

## 20. Repository-Struktur

```
Resilienz.AI/
├── agent/                      # KI-Agent-Kern
│   ├── brain.py               # RAgent-Orchestrierung
│   ├── auditing.py            # Hybrid-Audit-Logik
│   ├── tools.py               # Werkzeugdefinitionen (LLM-aufrufbar)
│   ├── prompts.py             # Prompt-Engineering
│   └── llm/                   # LLM-Integration
│       ├── ai_engine.py       # OpenRouter-Anbieter
│       ├── switch.py          # Modell-Failover-Logik
│       ├── base.py            # Abstrakte Basisklasse
│       ├── factory.py         # Modelfabrik
│       └── utils.py           # Token-Management-Werkzeuge
│
├── api/                       # Backend-API
│   └── app.py                 # Flask-Server + SSE
│
├── dashboard/                 # Frontend
│   ├── index.html             # Hauptdashboard
│   ├── app.js                 # UI-Logik + API-Aufrufe
│   └── style.css              # Glassmorphism-Styling
│
├── data/                      # Datenschicht
│   ├── resilienz.db           # SQLite-Datenbank
│   ├── vector_store/          # ChromaDB-Vektorspeicher
│   ├── generate_data.py       # Datengenerierungsskript
│   └── map_data.py            # Geografische Zuordnungen
│
├── alerts/                    # Benachrichtigungssystem
│   ├── notifier.py            # E-Mail-Warnungen
│   └── pdf_generator.py       # PDF-Berichtserstellung
│
├── tests/                     # Testsuite
│   ├── agent/                 # Agent-Tests
│   ├── api/                  # API-Tests
│   └── alerts/               # Alert-Tests
│
├── config.py                  # Zentrale Konfiguration
├── requirements.txt           # Python-Abhängigkeiten
├── README.md                  # Projektdokumentation (Englisch)
├── README_DE.md               # Projektdokumentation (Deutsch)
└── .env.example               # Umgebungsvorlage
```

---

## 21. Demo und Video

> 📺 **Live-Demo verfügbar**
>
> Eine funktionierende Demonstration des vollständigen Workflows von Risikoerkennung bis Szenariosimulation ist verfügbar.
>
> **Video ansehen**: [my youtube demo link]
>
> **GIF-Vorschau**: Das Dashboard aktualisiert sich automatisch bei Szenarioauslösung, mit Echtzeit-Kartenvisualisierung und Thought-Trace-Streaming.

---

## 22. Über den Autor

**Balaji Addanki** — KI/ML-Ingenieur mit Spezialisierung auf autonome Agentensysteme und Lieferkettenintelligenz.

**Resilienz.AI** wurde als Demonstration einer produktionsinspirierten KI-Agentenarchitektur entwickelt, mit Fokus auf:

- **Multi-Modell-LLM-Orchestrierung**: Resiliente Failover-Systeme mit OpenRouter
- **Hybride KI-Pipelines**: Kombination von deterministischer Python-Logik mit LLM-Schlussfolgerungen
- **Erklärbare KI**: Echtzeit-Though-Trace-Streaming für Transparenz
- **Lieferkettenintelligenz**: Domänenspezifische Agentenwerkzeuge für Beschaffungsrisikomanagement

Dieses Projekt zeigt Fähigkeiten in:

- KI-Agentenarchitektur (ReAct-Schleifen, Werkzeugorchestrierung)
- Full-Stack-Entwicklung (Flask + Vanilla JS)
- Data Engineering (SQLite + ChromaDB-Hybrid)
- Prompt Engineering (Optimierte kontextbewusste Systeme)

---

*Mit Produktionsmustern gebaut für die deutsche Fertigungsindustrie 🏭🇩🇪*
