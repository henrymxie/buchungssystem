# Python-Buchungssystem (ERP-Prototyp)

Ein funktionsfähiges, dreischichtiges Buchungssystem mit integrierter Finanzanalyse, entwickelt im Rahmen des Moduls **ABV-Programmieren für WiWiss** an der **Freien Universität Berlin**.

## Architektur
Das Projekt folgt einer strikten Trennung der Zuständigkeiten (3-Tier-Architektur):
* **Frontend:** Streamlit (Darstellung, Nutzerinteraktion und Session-basiertes Login)
* **Backend:** FastAPI mit Pydantic (Validierung der Geschäftslogik und REST-Endpunkte)
* **Datenbank:** SQLite (Persistente Speicherung via `sqlite3`)
* **Auswertung & Analytik:** Pandas (Aggregationen, GuV, Bilanzierung)

Das Frontend kommuniziert ausschließlich über HTTP-Requests (`requests`) mit der REST-API des Backends. Direkte Datenbankzugriffe durch den Client sind systemisch ausgeschlossen.

## Features (inkl. kreativer Erweiterungen)
Neben den CRUD-Basisoperationen für Einnahmen und Ausgaben bietet das System tiefgehende betriebswirtschaftliche Auswertungen:
* **Rollenbasiertes Zugangssystem:** Trennung von Administratoren (voller Analyse-Zugriff) und regulären Usern (nur Datenerfassung).
* **Vollständige Finanzübersicht:** Aggregierte Gewinn- und Verlustrechnung (GuV) sowie eine stichtagsbezogene Bilanz (Aktiva/Passiva) mit Kontenrahmen.
* **Predictive Forecast:** Ein in Pandas integriertes Prognosemodell, das historische Tagesdurchschnitte auswertet und einen 30-Tage-Trend berechnet.
* **ERP-Funktionalitäten:** Verwaltung von Geschäftspartnern, Kostenstellen und Verfolgung von unbezahlten Rechnungen (Offene Posten).
* **Demo-Daten-Generator:** Automatisierte Erstellung von realistischen Testdaten für eine sofort aussagekräftige Visualisierung.

## Starten des Projekts
Das Projekt nutzt `uv` für das Abhängigkeitsmanagement.

1. **Backend starten (Terminal 1):**
uv run uvicorn backend.main:app --reload

2. **Frontend starten (Terminal 2):**
uv run streamlit run frontend/app.py
- Die interaktive API-Dokumentation ist unter http://127.0.0.1:8000/docs erreichbar.
- Die Weboberfläche öffnet sich unter http://localhost:8501.

# KI-Nutzungserklärung (AI Usage)

In diesem Projekt wurde Künstliche Intelligenz gezielt als Unterstützung für Architektur-Entscheidungen, Pair-Programming und Code-Vervollständigung eingesetzt. Die konzeptionelle Ausarbeitung und Systemintegration erfolgten eigenständig.

**Eingesetzte Tools:**
1. **GitHub Copilot:**
   * **Einsatzgebiet:** Inline-Code-Vervollständigung, Generierung von Boilerplate-Code (z.B. Pydantic-Modelle, einfache FastAPI-Routen) und Syntax-Hilfe beim Schreiben der UI-Elemente in Streamlit.
2. **Claude & Gemini:**
   * **Einsatzgebiet:** Architektur-Beratung und Pair-Programming.
   * **Konkrete Anwendung:** Diskussion über die saubere Trennung von Frontend, Backend und Datenbank (3-Tier-Architektur). Unterstützung beim Refactoring von komplexen Daten-Aggregationen mit `pandas` (z.B. für die Bilanzierung, Top-Partner-Analysen und Offene Posten) sowie beim Debugging von Python-Einrückungsfehlern und dem Auflösen veralteter Streamlit-Warnungen.

**Eigenleistung & Konzept:**
Die Definition der fachlichen Anforderungen, sowie das relationale Datenmodell lagen vollständig bei mir. Dazu gehört das Design der betriebswirtschaftlichen Logik (Unterscheidung zwischen GuV und Bilanz, Forecast-Methodik) sowie die Orchestrierung der einzelnen Schichten. Die KI-Modelle fungierten als "Smart Assistants", um die von mir erdachte Struktur technisch effizient in Code zu wandeln.