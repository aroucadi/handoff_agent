"""
Graph Generator — Tenant-Aware Ingest Endpoint

Universal webhook receiver that accepts payloads from any CRM platform.
For each incoming webhook:
1. Looks up tenant config from Firestore
2. Verifies HMAC-SHA256 webhook signature
3. Applies the tenant's field mapping to normalize the payload
4. Writes a deal summary to Firestore (for the Voice UI dashboard)
5. Forwards to the existing graph generation pipeline
"""

from __future__ import annotations

import hmac
import hashlib
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from google.cloud import firestore

from field_mapper import apply_field_mapping, validate_mapping_result

log = logging.getLogger("graph-generator.ingest")

router = APIRouter()
db = firestore.Client()


def _verify_signature(payload_bytes: bytes, secret: str, signature: str) -> bool:
    """Verify HMAC-SHA256 webhook signature."""
    if not secret or not signature:
        return False
    expected = hmac.new(
        secret.encode("utf-8"), payload_bytes, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/ingest/{tenant_id}")
async def ingest_webhook(
    tenant_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Universal webhook receiver for any CRM platform.

    Accepts raw JSON, applies tenant-specific field mapping, and triggers
    graph generation. This is the URL that tenants paste into their CRM's
    outbound webhook configuration.
    """
    # 1. Look up tenant config
    tenant_doc = db.collection("tenants").document(tenant_id).get()
    if not tenant_doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")

    tenant = tenant_doc.to_dict()
    webhook_secret = tenant.get("webhook_secret", "")
    field_mapping = tenant.get("crm", {}).get("field_mapping", {})
    brand_name = tenant.get("brand_name", "Unknown")

    # 2. Verify signature (optional — skip if no signature header)
    payload_bytes = await request.body()
    signature = request.headers.get("X-Webhook-Signature", "")

    if webhook_secret and signature:
        if not _verify_signature(payload_bytes, webhook_secret, signature):
            log.warning(f"[INGEST] Invalid signature for tenant {tenant_id}")
            raise HTTPException(401, "Invalid webhook signature")
    elif webhook_secret and not signature:
        # Signature expected but not provided — log warning but allow
        # (graceful degradation for initial setup / testing)
        log.warning(f"[INGEST] No signature provided for tenant {tenant_id} (expected)")

    # 3. Parse and apply field mapping
    import json
    raw_payload = json.loads(payload_bytes)

    if field_mapping:
        normalized = apply_field_mapping(raw_payload, field_mapping)
    else:
        # No mapping configured — assume payload is already in internal format
        normalized = raw_payload

    # Inject tenant metadata
    normalized["_tenant_id"] = tenant_id
    normalized["_brand_name"] = brand_name
    normalized["_ingested_at"] = _now_iso()

    # 4. Validate the normalized payload
    warnings = validate_mapping_result(normalized)
    if any(w.startswith("REQUIRED:") for w in warnings):
        log.error(f"[INGEST] Missing required fields: {warnings}")
        # Update integration status to error
        db.collection("tenants").document(tenant_id).update({
            "integration_status": "error",
            "updated_at": _now_iso(),
        })
        return JSONResponse(
            status_code=422,
            content={
                "error": "Missing required fields after mapping",
                "warnings": warnings,
                "normalized_preview": {k: v for k, v in normalized.items() if not k.startswith("_")},
            },
        )

    # 5. Write deal summary to Firestore (for Voice UI dashboard)
    deal_id = normalized.get("deal_id", f"deal-{tenant_id[:8]}")
    company_name = normalized.get("company_name", "Unknown Company")
    client_id = company_name.lower().replace(" ", "-").replace(",", "").replace(".", "")

    deal_summary = {
        "deal_id": deal_id,
        "tenant_id": tenant_id,
        "client_id": client_id,
        "company_name": company_name,
        "deal_value": normalized.get("deal_value", 0),
        "close_date": normalized.get("close_date", ""),
        "industry": normalized.get("industry", ""),
        "stage": "closed_won",
        "products": normalized.get("products", []),
        "contacts": normalized.get("contacts", []),
        "graph_ready": False,  # Will be updated after generation
        "ingested_at": _now_iso(),
    }

    db.collection("deals").document(tenant_id).collection("items").document(deal_id).set(deal_summary)
    log.info(f"[INGEST] Persisted deal summary: deals/{tenant_id}/items/{deal_id}")

    # 6. Update integration status to verified (first successful ingest)
    current_status = tenant.get("integration_status", "not_configured")
    if current_status in ("not_configured", "pending", "error"):
        db.collection("tenants").document(tenant_id).update({
            "integration_status": "verified",
            "updated_at": _now_iso(),
        })

    # 7. Forward to graph generation pipeline
    from main import _run_generation, jobs
    import uuid

    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "company_name": company_name,
        "deal_id": deal_id,
        "tenant_id": tenant_id,
        "started_at": _now_iso(),
    }

    async def _run_and_update_deal(job_id: str, payload: dict):
        """Run generation and update deal summary when complete."""
        await _run_generation(job_id, payload)
        # After generation, update the deal's graph_ready flag
        job = jobs.get(job_id, {})
        if job.get("status") == "complete":
            db.collection("deals").document(tenant_id).collection("items").document(deal_id).update({
                "graph_ready": True,
                "node_count": job.get("node_count", 0),
            })
            log.info(f"[INGEST] Deal {deal_id} graph_ready=True, nodes={job.get('node_count', 0)}")

    background_tasks.add_task(_run_and_update_deal, job_id, normalized)

    log.info(f"[INGEST] Accepted webhook for tenant {tenant_id}, job {job_id}")

    return JSONResponse(
        status_code=202,
        content={
            "status": "accepted",
            "job_id": job_id,
            "tenant_id": tenant_id,
            "company_name": company_name,
            "deal_id": deal_id,
            "mapping_warnings": [w for w in warnings if w.startswith("RECOMMENDED:")],
        },
    )
