# Daten-Ordner — Der Maschinenraum 🚂🗃️

Der Ordner `data/` speichert alle Informationen von Resilienz.AI. Es gibt zwei Wege: Genaue Zahlen (SQL) und Texte mit Sinn (Vector DB).

## 📄 Wichtige Teile

| Datei | Zweck |
|-------|-------|
| `resilienz.db` | **Fakten-Ebene (SQL)**: Eine SQLite Datenbank für Bestellungen, Lager und Lieferanten. |
| `vector_store/` | **Gedächtnis für Sinn**: Speicher (ChromaDB) für Weltnachrichten. |
| `map_data.py` | **Landkarte**: Gibt Städten von Lieferanten genaue Koordinaten für die Karte. |
| `generate_data.py` | **Das Herz der Daten**: Erstellt CSV-Dateien und füllt die Datenbanken. |

## 🧪 Peak Demo: Sicherheit bei Tests
Der Server nutzt "Schatten-Daten" im Speicher. So können wir Krisen testen, ohne die echte Datenbank (`resilienz.db`) zu ändern.

---

*Für technische Details gehen Sie zur Datei [2_datenarchitektur.md](../DE_documentation (in german)/2_datenarchitektur.md).*
