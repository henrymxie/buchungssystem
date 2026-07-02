#!/bin/sh
# Backend im Hintergrund starten – nur intern auf localhost erreichbar
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &

# Frontend im Vordergrund – Render gibt den öffentlichen Port über $PORT vor
streamlit run frontend/app.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT:-8501}" \
  --server.headless true