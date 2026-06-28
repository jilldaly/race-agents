# Hugging Face Space (Docker SDK) entrypoint for agent 01 — the stateless Cork
# City Marathon fact-checker. Built from a curated, PII-free tree: a pre-scrubbed
# silver db and no bronze PDFs, so the image holds zero personal data.
FROM python:3.11-slim

# HF Spaces run the container as a non-root user (uid 1000). Create it and keep all
# writable state (matplotlib cache, streamlit config, chart output) under its HOME.
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    MPLCONFIGDIR=/tmp/matplotlib \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

WORKDIR /app
COPY --chown=user packages/racedata packages/racedata
COPY --chown=user agents/01-stateless agents/01-stateless

RUN pip install --no-cache-dir -e packages/racedata -r agents/01-stateless/requirements.txt

USER user
WORKDIR /app/agents/01-stateless
RUN mkdir -p output

# Serve on HF's default port (7860) so routing works without relying on app_port.
EXPOSE 7860
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=7860"]
