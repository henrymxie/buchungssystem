# 📒 Buchungssystem – Dreischichtiges ERP mit Finanzanalyse

Ein funktionsfähiges Buchungssystem mit integrierter betriebswirtschaftlicher Auswertung, gebaut als sauber getrennte 3-Tier-Anwendung – von der CRUD-Erfassung über GuV, Bilanz und Cashflow bis zum containerisierten Live-Deployment.

> Ursprünglich entstanden im Modul *ABV-Programmieren für WiWiss* an der **Freien Universität Berlin**, seitdem eigenständig weiterentwickelt (CRUD, Docker, Konfigurationsmanagement, interaktive Charts, Cloud-Deployment).

## 🔗 Live-Demo

**➡️ ⟨https://gen-z-buchungen.onrender.com⟩**

> Hinweis: Die Demo läuft auf einem kostenlosen Server, der nach Inaktivität einschläft – der **erste Aufruf kann 30–60 Sekunden** dauern, danach ist sie flott. Demo-Daten werden beim Start automatisch geladen.

Zugangsdaten zum Ausprobieren:
- **Admin** (voller Zugriff auf alle Auswertungen): `hh` / `hh`
- **User** (nur Datenerfassung): `user` / `meinGeheimesUserPasswort`

## 📸 Screenshots

⟨hier ein bis zwei Screenshots einfügen, z. B. Dashboard und GuV⟩

<!-- Beispiel: ![Dashboard](docs/dashboard.png) -->

## ✨ Features

- **Rollenbasiertes Login** – Trennung von Admin (volle Analyse) und User (nur Erfassung), geprüft über das Backend.
- **Vollständiges CRUD** – Buchungen anlegen, bearbeiten und löschen über saubere REST-Endpunkte (`POST`, `PUT`, `DELETE`).
- **Betriebswirtschaftliche Auswertungen** – aggregierte Gewinn- und Verlustrechnung (GuV), stichtagsbezogene Bilanz (Aktiva/Passiva) und ein 30-Tage-Forecast auf Basis historischer Tagesdurchschnitte.
- **ERP-Analysen** – Monatsentwicklung, kumulierter Cashflow-Verlauf, Top-Kunden/-Lieferanten, offene Posten und Kosten je Kostenstelle.
- **Interaktive Diagramme** – alle Charts mit Plotly (Hover, Zoom, ein-/ausblendbare Legenden).
- **Demo-Daten-Generator** – realistische Testdaten auf Knopfdruck; im Deployment automatisch beim Start (`AUTO_SEED`).

## 🏗️ Architektur

Strikte Trennung der Zuständigkeiten (3-Tier). Das Frontend spricht **ausschließlich** über HTTP-Requests mit der REST-API – direkte Datenbankzugriffe des Clients sind systemisch ausgeschlossen.

| Schicht | Technologie | Aufgabe |
|---|---|---|
| **Frontend** | Streamlit + Plotly | Darstellung, Login, interaktive Charts |
| **Backend** | FastAPI + Pydantic | Validierung, Geschäftslogik, REST-Endpunkte |
| **Analytik** | Pandas | Aggregationen (GuV, Bilanz, Forecast) |
| **Datenbank** | SQLite | Persistente Speicherung |
| **Konfiguration** | pydantic-settings + `.env` | Zugangsdaten & Einstellungen außerhalb des Codes |

## 🛠️ Tech-Stack

Python 3.14 · FastAPI · Streamlit · Pandas · Plotly · Pydantic / pydantic-settings · SQLite · Docker & Docker Compose · uv (Dependency-Management) · Deployment auf Render

## 🚀 Lokal starten

### Variante A – mit Docker (empfohlen)

Voraussetzung: Docker Desktop läuft. Lege zunächst eine `.env` an (Vorlage siehe `.env.example`) und starte dann:

```bash
docker compose up -d --build
```

Die App öffnet sich unter **http://localhost:8501**, die API-Dokumentation unter **http://localhost:8000/docs**.
Stoppen mit `docker compose down`.

### Variante B – ohne Docker (mit uv)

```bash
# Terminal 1 – Backend
uv run uvicorn backend.main:app --reload

# Terminal 2 – Frontend
uv run streamlit run frontend/app.py
```

## 📁 Projektstruktur

```
buchungssystem/
├─ backend/
│  ├─ main.py          # FastAPI-Endpunkte
│  ├─ models.py        # Pydantic-Modelle
│  ├─ database.py      # SQLite-Zugriff
│  ├─ auswertung.py    # Finanzanalysen (Pandas)
│  ├─ demo_daten.py    # Demo-Datengenerator
│  └─ config.py        # Konfiguration (pydantic-settings)
├─ frontend/
│  └─ app.py           # Streamlit-Oberfläche
├─ .streamlit/
│  └─ config.toml      # Farb-Theme
├─ Dockerfile
├─ docker-compose.yml
├─ start.sh            # startet Backend + Frontend (Single-Service-Deployment)
├─ pyproject.toml
└─ README.md
```

## ☁️ Deployment

Deployt auf **Render** als einzelner Docker-Container: `start.sh` startet das Backend intern (`uvicorn` auf `127.0.0.1:8000`) und das Frontend öffentlich (`streamlit` auf dem von Render vorgegebenen Port). Jeder Push auf `main` löst automatisch ein neues Deployment aus. Zugangsdaten werden über Umgebungsvariablen gesetzt, nicht im Code hinterlegt.

## 🧭 Roadmap / mögliche Erweiterungen

- [ ] Migration von SQLite zu PostgreSQL für dauerhaft persistente Daten
- [ ] Automatisierte Tests mit pytest (v. a. für die Auswertungslogik)
- [ ] Echte Authentifizierung mit Passwort-Hashing (bcrypt) und JWT-Tokens

## 🤖 KI-Nutzungserklärung

Künstliche Intelligenz wurde gezielt als Pair-Programming-Unterstützung eingesetzt: für Architektur-Diskussionen, das Erklären neuer Werkzeuge (Docker, REST-Semantik, pydantic-settings) und Debugging. Die fachlichen Anforderungen, das Datenmodell und die betriebswirtschaftliche Logik sowie die Integration der einzelnen Bausteine lagen bei mir.