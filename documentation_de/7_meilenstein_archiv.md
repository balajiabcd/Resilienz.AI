# Resilienz.AI — Archiv der Meilensteine & Umsetzung 🏗️📖

Dieses Dokument zeigt die Geschichte des Projekts Resilienz.AI. Von der ersten Dashboard-Idee bis zur Peak Demo.

---

## 🚩 Meilenstein 1: Das Fundament
Bau der Grund-Struktur für die Datenbanken (**SQLite** und **ChromaDB**). Wir haben die interne Welt (Bestellungen) und die externe Welt (Nachrichten) gebaut.

## 🚩 Meilenstein 2: Die Werkzeugkiste (Tools)
Bau der **8 Python-Werkzeuge** für die KI (R_agent). Die KI kann jetzt das Lager prüfen, Weltnachrichten suchen und das Risiko berechnen (Zahl 0-100).

## 🚩 Meilenstein 3: Das Gehirn (Multi-LLM)
Verbindung mit der **Gemini 1.5 Flash** KI und dem **LLMSwitch**. Das bedeutet: Wenn eine KI nicht antwortet, nutzt der Agent automatisch eine andere (Grok, Qwen, etc.).

## 🚩 Meilenstein 4: Alarme & Aktionen
Bau des **Nachrichten-Systems** und der PDF-Berichte. Die KI kann jetzt E-Mails schicken, wenn ein Risiko groß ist.

## 🚩 Meilenstein 5: Das digitale Cockpit
Bau des **Dashboards** mit modernen Glas-Effekten. Funktionen sind:
-   **Live-Zahlen**: Aktuelle Lieferanten, Bestellungen und Verspätungen.
-   **Berichte**: KI-Berichte direkt auf der Webseite lesen.

---

## 🚩 Finale Phase: Die Peak Demo Erweiterungen
Das Projekt hat jetzt die "Peak Demo" Stufe erreicht (siehe `6_peak_demo_durchlauf.md` für Details):
1.  🌍 **Weltkarte**: Zeigt Orte mit einem Puls-Effekt für Risiken.
2.  🌋 **Stress-Test Center**: Interaktive Krisen (Suez, Streik) als **Simulationen im Speicher**.
3.  🧠 **KI-Gedanken-Spur**: Live-Streaming der Gedanken der KI über **SSE (Server-Sent Events)**.

---

## 📜 Archiv der Pläne
Die alten Pläne liegen im Ordner `implementation_plans/` (jetzt auch im `documentation/` Archiv):
-   `01_upgp_peak_demo_enhancements.md`: Strategie für die Peak Demo.
-   `multi_llm_plan.md`: Plan für die Sicherheit bei der KI (Fallbacks).
-   `token_limit_protection.md`: Plan für den Speicher der KI.
-   `milestone_5_dashboard_plan.md`: Architektur für die Webseite.
