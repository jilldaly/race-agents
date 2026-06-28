# Local / self-hosted container for agent 01.
# NOTE: this copies the raw bronze PDFs (which contain runner names) and builds
# silver from them — fine for local use, but the image holds PII. For a PUBLIC
# deploy use deploy/hf-space/ instead: it ships a pre-scrubbed, name-free silver
# db and no bronze (see ADR/JOURNAL — GDPR scrub).
# Build from the repo root:  docker build -f agents/01-stateless/Dockerfile -t agent01 .
FROM python:3.11-slim
WORKDIR /app

COPY packages/racedata packages/racedata
COPY data/bronze data/bronze
COPY agents/01-stateless agents/01-stateless

RUN pip install --no-cache-dir -e packages/racedata -r agents/01-stateless/requirements.txt

WORKDIR /app/agents/01-stateless
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
