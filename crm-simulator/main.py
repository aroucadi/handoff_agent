"""CRM Simulator — FastAPI Application.

A lightweight but fully functional CRM simulator for Handoff demos.
Supports deal CRUD, pipeline stage transitions, webhook dispatch on Closed Won,
and file uploads for contracts/transcripts.
"""

from __future__ import annotations

import os
import uuid
from copy import deepcopy
from datetime import date, datetime

import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import storage as gcs

from models import Deal, DealStage, DealUpdate, WebhookPayload
from seed_data import DEMO_DEALS

app = FastAPI(
    title="Handoff CRM Simulator",
    description="Lightweight CRM simulator for Handoff demos — manages deals, contacts, and fires webhooks on Closed Won",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory deal store (seeded from seed_data.py)
# In a real CRM this would be a database. For our simulator, in-memory is fine
# because the data is small and we reseed on restart.
# ---------------------------------------------------------------------------
deals_store: dict[str, Deal] = {}
webhook_log: list[dict] = []


def _seed_deals():
    """Load demo deals into the store."""
    for deal in DEMO_DEALS:
        deals_store[deal.deal_id] = deepcopy(deal)


_seed_deals()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "crm-simulator", "version": "0.1.0"}


# ---------------------------------------------------------------------------
# Deal CRUD
# ---------------------------------------------------------------------------
@app.get("/api/deals")
async def list_deals():
    """List all deals in the CRM."""
    return {
        "deals": [deal.model_dump(mode="json") for deal in deals_store.values()],
        "count": len(deals_store),
    }


@app.get("/api/deals/{deal_id}")
async def get_deal(deal_id: str):
    """Get a single deal by ID."""
    deal = deals_store.get(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")
    return deal.model_dump(mode="json")


@app.patch("/api/deals/{deal_id}")
async def update_deal(deal_id: str, update: DealUpdate):
    """Update a deal's fields."""
    deal = deals_store.get(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")

    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deal, field, value)
    deal.updated_at = datetime.utcnow()

    return deal.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Stage Transition (the critical action)
# ---------------------------------------------------------------------------
@app.post("/api/deals/{deal_id}/stage")
async def change_deal_stage(deal_id: str, stage: str):
    """Move a deal to a new pipeline stage.

    When moving to 'closed_won', automatically:
    1. Sets close_date to today
    2. Fires webhook to configured URL
    """
    deal = deals_store.get(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")

    try:
        new_stage = DealStage(stage)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid stage: {stage}. Valid stages: {[s.value for s in DealStage]}",
        )

    old_stage = deal.stage
    deal.stage = new_stage
    deal.updated_at = datetime.utcnow()

    result = {
        "deal_id": deal_id,
        "old_stage": old_stage.value,
        "new_stage": new_stage.value,
        "webhook_fired": False,
    }

    # Fire webhook on Closed Won transition
    if new_stage == DealStage.CLOSED_WON:
        deal.close_date = date.today()
        webhook_result = await _fire_webhook(deal)
        result["webhook_fired"] = True
        result["webhook_result"] = webhook_result

    return result


async def _fire_webhook(deal: Deal) -> dict:
    """Fire the Closed Won webhook to the Handoff backend."""
    if not deal.webhook_url:
        return {"status": "skipped", "reason": "No webhook_url configured"}

    payload = WebhookPayload(
        deal_id=deal.deal_id,
        company_name=deal.company_name,
        deal_value=deal.deal_value,
        products=[p.model_dump() for p in deal.products],
        close_date=str(deal.close_date or date.today()),
        sla_days=deal.sla_days,
        csm_id=deal.csm_id,
        industry=deal.industry,
        employee_count=deal.employee_count,
        contacts=[c.model_dump() for c in deal.contacts],
        risks=[r.model_dump() for r in deal.risks],
        success_metrics=[m.model_dump() for m in deal.success_metrics],
        sales_transcript=deal.sales_transcript,
        contract_pdf_url=deal.contract_pdf_url,
    )

    log_entry = {
        "id": str(uuid.uuid4()),
        "deal_id": deal.deal_id,
        "company_name": deal.company_name,
        "webhook_url": deal.webhook_url,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "pending",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                deal.webhook_url,
                json=payload.model_dump(),
                headers={"Content-Type": "application/json", "X-CRM-Event": "deal.closed_won"},
            )

        deal.webhook_fired = True
        deal.webhook_response = f"{response.status_code}: {response.text[:200]}"
        log_entry["status"] = "success"
        log_entry["response_status"] = response.status_code

        return {"status": "sent", "response_code": response.status_code}

    except Exception as e:
        deal.webhook_fired = True
        deal.webhook_response = f"ERROR: {str(e)}"
        log_entry["status"] = "failed"
        log_entry["error"] = str(e)

        return {"status": "failed", "error": str(e)}

    finally:
        webhook_log.append(log_entry)


# ---------------------------------------------------------------------------
# File Upload (contract PDFs → GCS)
# ---------------------------------------------------------------------------
UPLOADS_BUCKET = os.environ.get(
    "UPLOADS_BUCKET",
    f"{os.environ.get('PROJECT_ID', 'handoff-dev')}-handoff-uploads",
)


def _get_gcs_client() -> gcs.Client:
    """Get GCS client."""
    return gcs.Client(project=os.environ.get("PROJECT_ID", "handoff-dev"))


@app.post("/api/deals/{deal_id}/upload-contract")
async def upload_contract(deal_id: str, file: UploadFile = File(...)):
    """Upload a contract PDF to Google Cloud Storage.

    Writes to gs://{UPLOADS_BUCKET}/contracts/{deal_id}/{filename}
    and updates the deal's contract_pdf_url with the GCS URI.
    """
    deal = deals_store.get(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")

    file_ext = os.path.splitext(file.filename or "contract.pdf")[1]
    filename = f"{deal_id}_contract{file_ext}"
    content = await file.read()

    # Upload to GCS
    gcs_client = _get_gcs_client()
    bucket = gcs_client.bucket(UPLOADS_BUCKET)
    blob_path = f"contracts/{deal_id}/{filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_string(content, content_type="application/pdf")

    gcs_uri = f"gs://{UPLOADS_BUCKET}/{blob_path}"
    deal.contract_pdf_url = gcs_uri
    deal.updated_at = datetime.utcnow()

    print(f"[GCS] Uploaded contract: {gcs_uri} ({len(content)} bytes)")

    return {
        "deal_id": deal_id,
        "filename": filename,
        "size_bytes": len(content),
        "gcs_uri": gcs_uri,
    }


@app.post("/api/deals/{deal_id}/update-transcript")
async def update_transcript(deal_id: str, transcript: str = Form(...)):
    """Update the sales call transcript for a deal."""
    deal = deals_store.get(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")

    deal.sales_transcript = transcript
    deal.updated_at = datetime.utcnow()

    return {"deal_id": deal_id, "transcript_length": len(transcript)}


# ---------------------------------------------------------------------------
# Webhook Log
# ---------------------------------------------------------------------------
@app.get("/api/webhooks/log")
async def get_webhook_log():
    """View the history of fired webhooks."""
    return {"log": webhook_log, "count": len(webhook_log)}


# ---------------------------------------------------------------------------
# Reset (for demos)
# ---------------------------------------------------------------------------
@app.post("/api/reset")
async def reset_data():
    """Reset all deals to seed data. Useful for demo reruns."""
    deals_store.clear()
    webhook_log.clear()
    _seed_deals()
    return {"status": "reset", "deal_count": len(deals_store)}


# ---------------------------------------------------------------------------
# Serve uploaded files (legacy fallback)
# ---------------------------------------------------------------------------
_upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(_upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_upload_dir), name="uploads")
