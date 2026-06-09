# KI-Nutzungserklärung (AI Usage)

In diesem Projekt wurde Künstliche Intelligenz gezielt als Unterstützung für Architektur-Entscheidungen, Pair-Programming und Code-Vervollständigung eingesetzt. Die konzeptionelle Ausarbeitung und Systemintegration erfolgten eigenständig.

**Eingesetzte Tools:**
1. **GitHub Copilot:**
   * **Einsatzgebiet:** Inline-Code-Vervollständigung, Generierung von Boilerplate-Code (z.B. Pydantic-Modelle, einfache FastAPI-Routen) und Syntax-Hilfe beim Schreiben der UI-Elemente in Streamlit.
2. **Claude & Gemini:**
   * **Einsatzgebiet:** Architektur-Beratung und Pair-Programming.
   * **Konkrete Anwendung:** Diskussion über die saubere Trennung von Frontend, Backend und Datenbank (3-Tier-Architektur). Unterstützung beim Refactoring von komplexen Daten-Aggregationen mit `pandas` (z.B. für die Bilanzierung, Top-Partner-Analysen und Offene Posten) sowie beim Debugging von Python-Einrückungsfehlern und dem Auflösen veralteter Streamlit-Warnungen.

**Eigenleistung & Konzept:**
Die Definition der fachlichen Anforderungen, die Auswahl der Architektur (FastAPI + Streamlit) sowie das relationale Datenmodell lagen vollständig bei mir. Dazu gehört das Design der betriebswirtschaftlichen Logik (Unterscheidung zwischen GuV und Bilanz, Forecast-Methodik) sowie die Orchestrierung der einzelnen Schichten. Die KI-Modelle fungierten als "Smart Assistants", um die von mir erdachte Struktur technisch effizient in Code zu gießen.