FROM python:3.11-slim

# STREAMLIT_CLIENT_*: this image is customer-facing, so no tracebacks in the
# browser (they still go to the logs) and no developer toolbar items like "Deploy".
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8501 \
    STREAMLIT_CLIENT_SHOW_ERROR_DETAILS=none \
    STREAMLIT_CLIENT_TOOLBAR_MODE=viewer

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN useradd --create-home --uid 10001 app && chown -R app /app
USER app

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",\"8501\")}/_stcore/health', timeout=4)"

# Apply database migrations, then start the app on the port the host provides.
# `exec` makes Streamlit PID 1 so it receives SIGTERM and shuts down cleanly on redeploys.
CMD ["sh", "-c", "alembic upgrade head && exec streamlit run dashboard/app.py --server.port=\"${PORT}\" --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false"]
