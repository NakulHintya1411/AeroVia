"""Docker HEALTHCHECK: probe whichever service this container runs."""
import os
import sys
import urllib.request

path = "/healthz" if os.environ.get("AEROVIA_SERVICE", "web") == "api" else "/_stcore/health"
url = f"http://127.0.0.1:{os.environ.get('PORT', '8501')}{path}"
try:
    with urllib.request.urlopen(url, timeout=4) as r:
        sys.exit(0 if r.status == 200 else 1)
except Exception:
    sys.exit(1)
