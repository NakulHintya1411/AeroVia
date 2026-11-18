"""AeroVia API service.

Run with:  uvicorn api.main:app --host 0.0.0.0 --port 8000

Endpoints
  GET  /healthz             liveness check
  POST /webhooks/razorpay   Razorpay subscription webhooks
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from db import init_db
from services import billing

log = logging.getLogger("aerovia.api")

MAX_WEBHOOK_BYTES = 1_000_000


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await run_in_threadpool(init_db)
    yield


app = FastAPI(title="AeroVia API", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request) -> JSONResponse:
    body = await request.body()
    if len(body) > MAX_WEBHOOK_BYTES:
        return JSONResponse({"error": "payload too large"}, status_code=413)
    signature = request.headers.get("x-razorpay-signature")
    event_id = request.headers.get("x-razorpay-event-id")
    try:
        outcome = await run_in_threadpool(billing.handle_webhook, body, signature, event_id)
    except billing.InvalidWebhookSignature:
        log.warning("Rejected Razorpay webhook with an invalid signature")
        return JSONResponse({"error": "invalid signature"}, status_code=400)
    except billing.WebhookNotConfigured:
        log.error("Razorpay webhook received but RAZORPAY_WEBHOOK_SECRET is not set")
        return JSONResponse({"error": "webhooks not configured"}, status_code=503)
    except ValueError:  # malformed JSON despite a valid signature
        log.warning("Razorpay webhook body was not valid JSON")
        return JSONResponse({"error": "invalid payload"}, status_code=400)
    except Exception:
        # Anything else (provider unreachable, database down): answer 5xx so Razorpay retries.
        log.exception("Failed to process Razorpay webhook %s", event_id)
        return JSONResponse({"error": "processing failed"}, status_code=500)
    return JSONResponse({"status": outcome})
