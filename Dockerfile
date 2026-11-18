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

# Strip Windows line endings in case the build context came from a CRLF checkout.
RUN sed -i 's/\r$//' scripts/start.sh \
    && useradd --create-home --uid 10001 app && chown -R app /app
USER app

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD ["python", "scripts/healthcheck.py"]

# One image, two services: AEROVIA_SERVICE=web (default, Streamlit) or api (webhooks).
# start.sh applies migrations, then `exec`s the server so it is PID 1 and receives
# SIGTERM for clean shutdowns on redeploys.
CMD ["sh", "scripts/start.sh"]
