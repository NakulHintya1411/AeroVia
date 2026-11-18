#!/bin/sh
# Container entrypoint. AEROVIA_SERVICE picks what to run:
#   web (default)  the Streamlit app
#   api            the FastAPI service (payment webhooks)
set -e

# Apply migrations (serialised with a Postgres advisory lock, so both services can start together).
python -c "from db import init_db; init_db()"

case "${AEROVIA_SERVICE:-web}" in
  web)
    exec streamlit run dashboard/app.py \
      --server.port="${PORT}" \
      --server.address=0.0.0.0 \
      --server.headless=true \
      --browser.gatherUsageStats=false
    ;;
  api)
    exec uvicorn api.main:app \
      --host 0.0.0.0 \
      --port "${PORT}" \
      --proxy-headers \
      --forwarded-allow-ips="*" \
      --no-server-header
    ;;
  *)
    echo "Unknown AEROVIA_SERVICE '${AEROVIA_SERVICE}' (expected 'web' or 'api')" >&2
    exit 1
    ;;
esac
