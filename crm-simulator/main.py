"""CRM Simulator Ã¢â‚¬â€ FastAPI Application.

A lightweight but fully functional CRM simulator for Synapse demos.
Supports deal CRUD, pipeline stage transitions, webhook dispatch on Closed Won,
and file uploads for contracts/transcripts.
"""

from __future__ import annotations

import os
import sys
import uuid
from copy import deepcopy
from datetime import date, datetime

import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse as FastFileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from google.cloud import storage as gcs

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.db import get_firestore_client

from models import Deal, DealCreate, DealStage, DealUpdate, WebhookPayload

app = FastAPI(
    title="ClawdForce CRM Simulator",
    description="Lightweight CRM simulator for Synapse demos Ã¢â‚¬â€ manages deals, contacts, and fires webhooks on Closed Won",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Firestore deal store
# ---------------------------------------------------------------------------
def _get_deal_doc(deal_id: str):
    db = get_firestore_client()
    return db.collection("crm_deals").document(deal_id)

def _get_webhook_col():
    db = get_firestore_client()
    return db.collection("crm_webhooks")


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "clawdforce-crm", "version": "4.0.0"}


# ---------------------------------------------------------------------------
# Deal CRUD
# ---------------------------------------------------------------------------
@app.get("/api/deals")
async def list_deals():
    """List all deals in the CRM."""
    db = get_firestore_client()
    docs = db.collection("crm_deals").stream()
    deals = [doc.to_dict() for doc in docs]
    return {
        "deals": deals,
        "count": len(deals),
    }


@app.post("/api/deals")
async def create_deal(req: DealCreate):
    deal_id = req.deal_id or f"OPP-{datetime.utcnow().year}-{uuid.uuid4().hex[:4].upper()}"
    doc_ref = _get_deal_doc(deal_id)
    if doc_ref.get().exists:
        raise HTTPException(status_code=409, detail=f"Deal {deal_id} already exists")

    payload = req.model_dump()
    payload["deal_id"] = deal_id
    deal = Deal(**payload)
    deal.updated_at = datetime.utcnow()
    doc_ref.set(deal.model_dump(mode="json"))
    return deal.model_dump(mode="json")


@app.get("/api/deals/{deal_id}")
async def get_deal(deal_id: str):
    """Get a single deal by ID."""
    doc = _get_deal_doc(deal_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")
    return doc.to_dict()


@app.patch("/api/deals/{deal_id}")
async def update_deal(deal_id: str, update: DealUpdate):
    """Update a deal's fields."""
    doc_ref = _get_deal_doc(deal_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")

    deal = Deal(**doc.to_dict())
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deal, field, value)
    deal.updated_at = datetime.utcnow()

    doc_ref.set(deal.model_dump(mode="json"))
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
    doc_ref = _get_deal_doc(deal_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")
        
    deal = Deal(**doc.to_dict())

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

    # Set close_date if closed won
    if new_stage == DealStage.CLOSED_WON:
        deal.close_date = date.today()
        
    doc_ref.set(deal.model_dump(mode="json"))
        
    # Fire webhook on ALL transitions to keep the Graph holistic
    webhook_result = await _fire_webhook(deal, doc_ref)
    result["webhook_fired"] = True
    result["webhook_result"] = webhook_result

    return result


async def _fire_webhook(deal: Deal, doc_ref) -> dict:
    """Fire a webhook using CRM platform emulation.

    Resolves the webhook target from:
    1. Tenant config in Firestore (if tenant_id is set)
    2. SYNAPSE_WEBHOOK_URL environment variable
    3. Deal's webhook_url property
    """
    db = get_firestore_client()

    # Resolve webhook target
    webhook_target = None

    # Priority 1: Tenant-aware routing via Firestore
    if deal.tenant_id:
        try:
            tenant_doc = db.collection("tenants").document(deal.tenant_id).get()
            if tenant_doc.exists:
                webhook_target = tenant_doc.to_dict().get("webhook_url")
                print(f"🔗 Resolved webhook URL from tenant config: {webhook_target}")
        except Exception as e:
            print(f"⚠️ Failed to resolve tenant webhook URL: {e}")

    # Priority 2 & 3: Environment or deal property
    if not webhook_target:
        webhook_target = os.environ.get("SYNAPSE_WEBHOOK_URL") or deal.webhook_url

    if not webhook_target:
        print(f"⚠️ Webhook skipped for {deal.deal_id} - no URL configured")
        return {"status": "skipped", "reason": "No webhook_url configured"}

    # Gather historical deals for text synthesis in Graph Generator
    historical_deals = []
    docs = db.collection("crm_deals").stream()
    for other_doc in docs:
        other_deal = Deal(**other_doc.to_dict())
        if other_deal.deal_id != deal.deal_id and other_deal.company_name.strip().lower() == deal.company_name.strip().lower():
            historical_deals.append({
                "deal_id": other_deal.deal_id,
                "stage": other_deal.stage.value,
                "deal_value": other_deal.deal_value,
                "close_date": str(other_deal.close_date) if other_deal.close_date else None,
                "products": [p.model_dump() for p in other_deal.products],
                "risks": [r.model_dump() for r in other_deal.risks]
            })

    # Build the internal payload
    internal_payload = {
        "deal_id": deal.deal_id,
        "company_name": deal.company_name,
        "deal_value": deal.deal_value,
        "stage": deal.stage.value,
        "products": [p.model_dump() for p in deal.products],
        "close_date": str(deal.close_date or date.today()),
        "sla_days": deal.sla_days,
        "csm_id": deal.csm_id,
        "industry": deal.industry,
        "employee_count": deal.employee_count,
        "contacts": [c.model_dump() for c in deal.contacts],
        "risks": [r.model_dump() for r in deal.risks],
        "success_metrics": [m.model_dump() for m in deal.success_metrics],
        "sales_transcript": deal.sales_transcript,
        "contract_pdf_url": deal.contract_pdf_url,
        "contract_file_uri": deal.contract_pdf_url,
        "historical_deals": historical_deals,
    }

    # Apply platform emulation — transform to CRM-specific format
    crm_platform = deal.crm_platform or "custom"
    emitted_payload = internal_payload

    log_id = str(uuid.uuid4())
    log_entry = {
        "id": log_id,
        "deal_id": deal.deal_id,
        "company_name": deal.company_name,
        "webhook_url": webhook_target,
        "crm_platform": crm_platform,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "pending",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"🚀 Firing {crm_platform.upper()} webhook to: {webhook_target} for {deal.deal_id}")
            response = await client.post(
                webhook_target,
                json=emitted_payload,
                headers={
                    "Content-Type": "application/json",
                    "X-CRM-Event": f"deal.stage_changed.{deal.stage.value}",
                    "X-CRM-Platform": crm_platform,
                },
            )

        deal.webhook_fired = True
        deal.webhook_response = f"{response.status_code}: {response.text[:200]}"
        log_entry["status"] = "success"
        log_entry["response_status"] = response.status_code

        return {"status": "sent", "response_code": response.status_code, "platform": crm_platform}

    except Exception as e:
        deal.webhook_fired = True
        deal.webhook_response = f"ERROR: {str(e)}"
        log_entry["status"] = "failed"
        log_entry["error"] = str(e)

        return {"status": "failed", "error": str(e)}

    finally:
        doc_ref.set(deal.model_dump(mode="json"))
        _get_webhook_col().document(log_id).set(log_entry)



# ---------------------------------------------------------------------------
# File Upload (contract PDFs Ã¢â€ â€™ GCS)
# ---------------------------------------------------------------------------
UPLOADS_BUCKET = os.environ.get(
    "UPLOADS_BUCKET",
    f"{os.environ.get('PROJECT_ID', 'synapse-488201')}-synapse-uploads",
)


def _get_gcs_client() -> gcs.Client:
    """Get GCS client."""
    return gcs.Client(project=os.environ.get("PROJECT_ID", "synapse-488201"))


@app.post("/api/deals/{deal_id}/upload-contract")
async def upload_contract(deal_id: str, file: UploadFile = File(...)):
    """Upload a contract PDF to Google Cloud Storage.

    Writes to gs://{UPLOADS_BUCKET}/contracts/{deal_id}/{filename}
    and updates the deal's contract_pdf_url with the GCS URI.
    """
    doc_ref = _get_deal_doc(deal_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")

    deal = Deal(**doc.to_dict())

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

    doc_ref.set(deal.model_dump(mode="json"))

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
    doc_ref = _get_deal_doc(deal_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail=f"Deal {deal_id} not found")

    deal = Deal(**doc.to_dict())
    deal.sales_transcript = transcript
    deal.updated_at = datetime.utcnow()

    doc_ref.set(deal.model_dump(mode="json"))

    return {"deal_id": deal_id, "transcript_length": len(transcript)}


# ---------------------------------------------------------------------------
# Webhook Log
# ---------------------------------------------------------------------------
@app.get("/api/webhooks/log")
async def get_webhook_log():
    """View the history of fired webhooks."""
    docs = _get_webhook_col().order_by("timestamp", direction="DESCENDING").limit(100).stream()
    log_data = [d.to_dict() for d in docs]
    return {"log": log_data, "count": len(log_data)}


# ---------------------------------------------------------------------------
# Contract PDF Viewer
# ---------------------------------------------------------------------------
@app.get("/api/deals/{deal_id}/contract-pdf")
async def get_contract_pdf(deal_id: str):
    """Serve the local contract PDF for inline viewing."""
    contracts_dir = os.path.join(os.path.dirname(__file__), "uploads", "contracts")
    pdf_path = os.path.join(contracts_dir, f"{deal_id}_contract.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"Contract PDF not found for {deal_id}")
    return FastFileResponse(pdf_path, media_type="application/pdf")


# ---------------------------------------------------------------------------
# Reset (for demos)
# ---------------------------------------------------------------------------
@app.post("/api/reset")
async def reset_data():
    """Reset all deals to seed data. Useful for demo reruns."""
    return {"status": "no_op", "message": "Reset handles via cleanup script and journey runner"}


# ---------------------------------------------------------------------------
# Serve Frontend & Uploads
# ---------------------------------------------------------------------------
_upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(_upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_upload_dir), name="uploads")

# Serve the React frontend (built in frontend/dist)
_frontend_dir = os.path.join(os.path.dirname(__file__), "frontend", "dist")
print(f"[CRM] Looking for frontend at: {_frontend_dir} (Exists: {os.path.exists(_frontend_dir)})")

@app.get("/", include_in_schema=False)
async def serve_index():
    index_path = os.path.join(_frontend_dir, "index.html")
    if os.path.exists(index_path):
        from fastapi.responses import FileResponse
        return FileResponse(index_path)
    return {"message": "ClawdForce CRM Simulator API. Frontend not found.", "frontend_path": _frontend_dir}

if os.path.exists(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
