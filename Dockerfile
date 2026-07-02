# Basis-Image mit Python 3.14
FROM python:3.14-slim

# uv aus dem offiziellen uv-Image in unser Image kopieren
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Zuerst nur die Dependency-Dateien kopieren -> besseres Docker-Caching
COPY pyproject.toml uv.lock README.md ./

# Nur die Abhängigkeiten installieren, nicht das Projekt selbst bauen
RUN uv sync --frozen --no-install-project

# Jetzt den eigentlichen Code kopieren
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# venv in den PATH legen, damit "uvicorn"/"streamlit" direkt aufrufbar sind
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV MPLCONFIGDIR=/tmp/matplotlib

# Start-Skript fürs Single-Service-Deployment (z.B. Render) mitkopieren
COPY start.sh ./start.sh

# Standard-Startbefehl: Backend + Frontend zusammen.
# (Lokal überschreibt docker-compose.yml diesen Befehl weiterhin.)
CMD ["sh", "start.sh"]