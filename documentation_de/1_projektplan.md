# Resilienz.AI — Projektplan & Architektur 🏗️

> **Status:** ✅ FERTIG — PEAK DEMO STATUS  
> **Letztes Update:** 22.03.2026  

Resilienz.AI hilft Firmen in Deutschland. Das Programm findet Probleme in der Lieferkette. Dieses Dokument erklärt den Plan und die Technik.

---

## 🔴 Das Problem: Reagieren vs. Proaktiv sein

### 1. Das Problem mit der Suche
Mitarbeiter in kleinen Firmen suchen oft lange nach Informationen. Sie brauchen 30% bis 40% ihrer Zeit dafür. Das ist zu viel Zeit für einfache Aufgaben.

### 2. Die Lücke bei der Information
Interne Systeme sind oft alt. Sie kennen keine neuen Probleme wie einen **Streik im Hamburger Hafen** oder eine **Sperrung im Suezkanal**. Das System erfährt die Probleme zu spät. Die Produktion stoppt dann.

### 3. Das Risiko bei kleinen Teilen
Kleine Teile wie ein Sensor für 5 Euro sind wichtig. Wenn ein Teil fehlt, kann eine Maschine für 50.000 Euro nicht fertig werden. Resilienz.AI hat einen "Plan B".

---

## 🏗️ Architektur in 4 Schichten

| Schicht | Name | Rolle |
|---------|------|-------|
| **1** | **Daten-Eingang** | Das Programm liest Daten aus Dateien (CSV) und Nachrichten. |
| **2** | **KI-Gehirn** | Die KI (Gemini) denkt nach. Sie findet Risiken. |
| **3** | **Aktion** | Das Programm schickt E-Mails und schreibt Berichte (PDF). |
| **4** | **Dashboard** | Eine Webseite für die Mitarbeiter. Dort sieht man alles. |

---

## 📁 Struktur des Projekts

```text
Resilienz.AI/
├── 📁 agent/          ← KI Logik und Werkzeuge.
├── 📁 api/            ← Der Server für die Webseite.
├── 📁 dashboard/      ← Die Webseite für den Nutzer.
├── 📁 data/           ← Alle Daten (Datenbanken).
├── 📁 documentation/  ← Hier sind die Erklärungen.
├── 📁 reports/        ← Berichte über Risiken (PDF).
├── 📁 tests/          ← Tests für das Programm.
└── config.py          ← Einstellungen.
```

---

## 📚 Meilensteine

1.  **Phase 1: Start**: Datenbanken bauen.
2.  **Phase 2: Werkzeuge**: Funktionen für die KI bauen.
3.  **Phase 3: Gehirn**: Die KI verbinden.
4.  **Phase 4: Nachrichten**: E-Mails und PDF bauen.
5.  **Phase 5: Peak Demo**: Die Weltkarte und Live-System bauen.

---

## 🎯 Philosophie

- **Transparenz**: Der Nutzer sieht, wie die KI denkt.
- **Sicherheit**: Tests verändern keine echten Daten.
- **Resilienz**: Wenn eine KI nicht arbeitet, nutzt das Programm eine andere KI.
