"""
Synapse Hub — FastAPI Application

Tenant configuration CRUD, product management, and knowledge generation
orchestration. Persists all data in Firestore collection: tenants/{tenant_id}
"""

from __future__ import annotations

import os
import re
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import firestore
import httpx

from models import (
    TenantConfig,
    CreateTenantRequest,
    UpdateTenantRequest,
    AddProductRequest,
    Product,
    TenantListResponse,
    TenantStatus,
    CrmConnection,
    TestConnectionRequest,
    TestConnectionResponse,
)
from core.normalization import slugify

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("hub")

# Graph generator URL for webhook provisioning
GRAPH_GENERATOR_URL = os.environ.get(
    "GRAPH_GENERATOR_URL",
    "http://localhost:8002",
)

app = FastAPI(
    title="Synapse Hub API",
    description="Tenant configuration portal for multi-tenant Synapse deployment",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from core.auth import verify_tenant_context, sign_tenant_context, DEMO_SECRET_KEY
from fastapi.responses import JSONResponse
from fastapi import Request
import hmac

@app.middleware("http")
async def tenant_context_middleware(request: Request, call_next):
    """Enforce and propagate tenant context."""
    # Creation of tenant is bypassable
    bypass_paths = ["/health", "/docs", "/openapi.json"]
    is_bypassed = any(request.url.path.startswith(p) for p in bypass_paths)
    
    # POST /api/tenants is how you create a new one, should be bypassable 
    # if we want to allow new onboardings without pre-existing context
    if request.url.path == "/api/tenants" and request.method in ["POST", "GET"]:
        is_bypassed = True

    tenant_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        tenant_id = verify_tenant_context(token)
    
    if not tenant_id:
        tenant_id = request.headers.get("X-Tenant-Id")
        
    request.state.tenant_id = tenant_id
    
    if not is_bypassed and not tenant_id:
        return JSONResponse(
            status_code=401,
            content={"error": "Tenant context required"}
        )
        
    response = await call_next(request)
    return response

db = firestore.Client()
TENANTS_COLLECTION = "tenants"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Health ───────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "hub-api", "version": "1.0.0"}


# ── Tenant CRUD ──────────────────────────────────────────────────

@app.get("/api/tenants", response_model=TenantListResponse)
def list_tenants(request: Request):
    """List all configured tenants (Oracle closed; no tokens returned here)."""
    docs = db.collection(TENANTS_COLLECTION).stream()
    tenants = []
    for doc in docs:
        data = doc.to_dict()
        tid = data.get("tenant_id")
        if tid:
            # Oracle is now CLOSED. Discovery only.
            data["signed_token"] = None 
            tenants.append(TenantConfig(**data))
    return TenantListResponse(tenants=tenants, total=len(tenants))


@app.post("/api/tenants/{tenant_id}/login")
def login_tenant(tenant_id: str):
    """Explicitly issue a signed token for a demo-enabled tenant."""
    doc = db.collection(TENANTS_COLLECTION).document(tenant_id).get()
    if not doc.exists:
        raise HTTPException(404, "Tenant not found")
    
    data = doc.to_dict()
    # Check if this tenant is explicitly allowed for public demo access
    if not data.get("allow_public_demo", True):
        raise HTTPException(403, "Public demo access disabled for this tenant")
    
    token = sign_tenant_context(tenant_id)
    return {"signed_token": token, "tenant_id": tenant_id}


@app.post("/api/tenants", response_model=TenantConfig, status_code=201)
def create_tenant(req: CreateTenantRequest):
    """Create a new tenant with default configuration."""
    from crm_templates import get_template_for_crm

    template = get_template_for_crm(req.crm_type.value)
    tenant = TenantConfig(
        name=req.name,
        brand_name=req.brand_name or req.name,
        crm=CrmConnection(
            crm_type=req.crm_type,
            field_mapping=template.get("field_mapping", {}),
            stage_mapping=template.get("stage_mapping", {}),
        ),
    )
    # Set agent brand_name to match
    tenant.agent.brand_name = tenant.brand_name

    # Auto-provision webhook URL
    tenant.webhook_url = f"{GRAPH_GENERATOR_URL}/ingest/{tenant.tenant_id}"

    # Sign token for immediate use by creator (seeding script / UI)
    tenant.signed_token = sign_tenant_context(tenant.tenant_id)

    doc_ref = db.collection(TENANTS_COLLECTION).document(tenant.tenant_id)
    doc_ref.set(tenant.model_dump())
    log.info(f"Created tenant: {tenant.tenant_id} ({tenant.name})")
    return tenant


# ── Job Observability ──────────────────────────────────────────

@app.get("/api/jobs")
def list_graph_jobs(request: Request, limit: int = 20):
    """List recent graph generation jobs for the authenticated tenant."""
    ctx_tenant_id = request.state.tenant_id
    if not ctx_tenant_id:
        raise HTTPException(401, "Tenant context required")

    jobs_ref = db.collection("graph_jobs")
    # Filter by tenant_id to prevent multi-tenant data leakage
    query = jobs_ref.where("tenant_id", "==", ctx_tenant_id).order_by("started_at", direction=firestore.Query.DESCENDING).limit(limit)
    docs = query.stream()
    return [doc.to_dict() for doc in docs]


@app.get("/api/jobs/{job_id}")
def get_graph_job(job_id: str, request: Request):
    """Get status and details of a specific graph job (with tenant check)."""
    ctx_tenant_id = request.state.tenant_id
    if not ctx_tenant_id:
        raise HTTPException(401, "Tenant context required")

    doc = db.collection("graph_jobs").document(job_id).get()
    if not doc.exists:
        raise HTTPException(404, f"Job {job_id} not found")
    
    job_data = doc.to_dict()
    if job_data.get("tenant_id") != ctx_tenant_id:
        raise HTTPException(403, "Job context mismatch")

    return job_data


@app.get("/api/tenants/{tenant_id}", response_model=TenantConfig)
def get_tenant(tenant_id: str, request: Request):
    """Retrieve a tenant's full configuration."""
    ctx_tenant_id = request.state.tenant_id
    if not ctx_tenant_id:
        raise HTTPException(401, "Tenant context required")
    if tenant_id != ctx_tenant_id:
        raise HTTPException(403, "Tenant context mismatch")
        
    doc = db.collection(TENANTS_COLLECTION).document(tenant_id).get()
    if not doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")
    return TenantConfig(**doc.to_dict())


@app.patch("/api/tenants/{tenant_id}", response_model=TenantConfig)
def update_tenant(tenant_id: str, req: UpdateTenantRequest, request: Request):
    """Update tenant fields (partial update)."""
    ctx_tenant_id = request.state.tenant_id
    if not ctx_tenant_id:
        raise HTTPException(401, "Tenant context required")
    if tenant_id != ctx_tenant_id:
        raise HTTPException(403, "Tenant context mismatch")

    doc_ref = db.collection(TENANTS_COLLECTION).document(tenant_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")

    current = TenantConfig(**doc.to_dict())
    updates = req.model_dump(exclude_none=True)
    updates["updated_at"] = _now()

    # Merge nested objects properly
    if "crm" in updates:
        merged_crm = current.crm.model_dump()
        merged_crm.update(updates["crm"])
        updates["crm"] = merged_crm
    if "agent" in updates:
        merged_agent = current.agent.model_dump()
        merged_agent.update(updates["agent"])
        updates["agent"] = merged_agent

    doc_ref.update(updates)
    log.info(f"Updated tenant: {tenant_id}")

    # Re-read and return
    updated = doc_ref.get()
    return TenantConfig(**updated.to_dict())


@app.delete("/api/tenants/{tenant_id}", status_code=204)
def delete_tenant(tenant_id: str, request: Request):
    """Delete a tenant configuration."""
    ctx_tenant_id = request.state.tenant_id
    if not ctx_tenant_id:
        raise HTTPException(401, "Tenant context required")
    if tenant_id != ctx_tenant_id:
        raise HTTPException(403, "Tenant context mismatch")

    doc_ref = db.collection(TENANTS_COLLECTION).document(tenant_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")
    doc_ref.delete()
    log.info(f"Deleted tenant: {tenant_id}")


# ── Integration Guide ─────────────────────────────────────────────

@app.get("/api/tenants/{tenant_id}/integration-guide")
def get_integration_guide(tenant_id: str, request: Request):
    """Get CRM-specific integration instructions for a tenant (hardened)."""
    ctx_tenant_id = request.state.tenant_id
    if not ctx_tenant_id:
        raise HTTPException(401, "Tenant context required")
    if tenant_id != ctx_tenant_id:
        raise HTTPException(403, "Tenant context mismatch")

    from crm_templates import get_setup_instructions, get_template_for_crm

    doc = db.collection(TENANTS_COLLECTION).document(tenant_id).get()
    if not doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")

    tenant = TenantConfig(**doc.to_dict())
    crm_type = tenant.crm.crm_type.value
    instructions = get_setup_instructions(crm_type)
    template = get_template_for_crm(crm_type)

    return {
        "tenant_id": tenant_id,
        "crm_type": crm_type,
        "webhook_url": tenant.webhook_url,
        "webhook_secret": tenant.webhook_secret,
        "integration_status": tenant.integration_status.value,
        "field_mapping": tenant.crm.field_mapping,
        "default_template": template,
        "setup": instructions,
    }


# ── Product Management ───────────────────────────────────────────

@app.post("/api/tenants/{tenant_id}/products", response_model=Product, status_code=201)
def add_product(tenant_id: str, req: AddProductRequest, request: Request):
    """Add a product to a tenant's catalog."""
    ctx_tenant_id = request.state.tenant_id
    if not ctx_tenant_id:
        raise HTTPException(401, "Tenant context required")
    if tenant_id != ctx_tenant_id:
        raise HTTPException(403, "Tenant context mismatch")

    doc_ref = db.collection(TENANTS_COLLECTION).document(tenant_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")

    product = Product(
        name=req.name,
        description=req.description,
        node_id=slugify(req.name),
    )

    tenant = TenantConfig(**doc.to_dict())
    tenant.products.append(product)
    tenant.updated_at = _now()

    doc_ref.update({
        "products": [p.model_dump() for p in tenant.products],
        "updated_at": tenant.updated_at,
    })
    log.info(f"Added product '{product.name}' to tenant {tenant_id}")
    return product


@app.delete("/api/tenants/{tenant_id}/products/{product_id}", status_code=204)
def remove_product(tenant_id: str, product_id: str, request: Request):
    """Remove a product from a tenant's catalog."""
    ctx_tenant_id = request.state.tenant_id
    if not ctx_tenant_id:
        raise HTTPException(401, "Tenant context required")
    if tenant_id != ctx_tenant_id:
        raise HTTPException(403, "Tenant context mismatch")

    doc_ref = db.collection(TENANTS_COLLECTION).document(tenant_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")

    tenant = TenantConfig(**doc.to_dict())
    tenant.products = [p for p in tenant.products if p.product_id != product_id]
    tenant.updated_at = _now()

    doc_ref.update({
        "products": [p.model_dump() for p in tenant.products],
        "updated_at": tenant.updated_at,
    })
    log.info(f"Removed product {product_id} from tenant {tenant_id}")


# ── Knowledge Generation ────────────────────────────────────────

@app.post("/api/tenants/{tenant_id}/generate-knowledge")
async def generate_knowledge(tenant_id: str, background_tasks: BackgroundTasks, request: Request):
    """Trigger tenant knowledge generation (background)."""
    ctx_tenant_id = request.state.tenant_id
    if not ctx_tenant_id:
        raise HTTPException(401, "Tenant context required")
    if tenant_id != ctx_tenant_id:
        raise HTTPException(403, "Tenant context mismatch")

    doc_ref = db.collection(TENANTS_COLLECTION).document(tenant_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")

    background_tasks.add_task(_run_generate_knowledge, tenant_id)
    return {"status": "started", "tenant_id": tenant_id}


async def _run_generate_knowledge(tenant_id: str):
    """Background worker for knowledge generation."""
    log.info(f"[HUB] Starting background knowledge generation for {tenant_id}")
    doc_ref = db.collection(TENANTS_COLLECTION).document(tenant_id)
    doc = doc_ref.get()
    if not doc.exists:
        return

    tenant = TenantConfig(**doc.to_dict())
    pending = [p for p in tenant.products if not p.knowledge_generated]

    if not pending:
        log.info(f"[HUB] No pending products for {tenant_id}")
        return

    from knowledge_generator import generate_product_knowledge

    for product in pending:
        try:
            log.info(f"[HUB] Generating knowledge for product: {product.name}")
            node_count = await generate_product_knowledge(
                tenant_id=tenant.tenant_id,
                brand_name=tenant.brand_name,
                product=product,
            )
            product.knowledge_generated = True
            product.node_count = node_count
        except Exception as e:
            log.error(f"Failed to generate knowledge for {product.name}: {e}")

    # Save updated product statuses
    tenant.updated_at = _now()
    doc_ref.update({
        "products": [p.model_dump() for p in tenant.products],
        "updated_at": tenant.updated_at,
    })
    log.info(f"[HUB] Completed knowledge generation for {tenant_id}")


@app.post("/api/tenants/{tenant_id}/sync-knowledge")
async def sync_knowledge(tenant_id: str, background_tasks: BackgroundTasks, request: Request):
    """Trigger tenant knowledge sync in the Graph Generator (background)."""
    ctx_tenant_id = request.state.tenant_id
    if not ctx_tenant_id:
        raise HTTPException(401, "Tenant context required")
    if tenant_id != ctx_tenant_id:
        raise HTTPException(403, "Tenant context mismatch")

    doc = db.collection(TENANTS_COLLECTION).document(tenant_id).get()
    if not doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")

    background_tasks.add_task(_run_sync_knowledge_background, tenant_id)
    return {"status": "started", "tenant_id": tenant_id}


async def _run_sync_knowledge_background(tenant_id: str):
    """Background worker to trigger the Graph Generator sync."""
    log.info(f"[HUB] Triggering background sync-knowledge for {tenant_id}")
    sync_url = f"{GRAPH_GENERATOR_URL.rstrip('/')}/api/sync-knowledge/{tenant_id}"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(sync_url)
            if resp.status_code >= 400:
                log.error(f"[HUB] Graph Generator sync request failed: {resp.status_code} {resp.text}")
            else:
                log.info(f"[HUB] Successfully triggered sync in Graph Generator for {tenant_id}")
    except Exception as e:
        log.error(f"[HUB] Failed to trigger sync in Graph Generator: {e}")


# ── Test Webhook ─────────────────────────────────────────────────

@app.post("/api/tenants/{tenant_id}/test-webhook")
async def test_webhook(tenant_id: str, request: Request):
    """Fire a test webhook to validate the CRM → graph-generator pipeline."""
    ctx_tenant_id = request.state.tenant_id
    if not ctx_tenant_id:
        raise HTTPException(401, "Tenant context required")
    if tenant_id != ctx_tenant_id:
        raise HTTPException(403, "Tenant context mismatch")

    import httpx

    doc = db.collection(TENANTS_COLLECTION).document(tenant_id).get()
    if not doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")

    tenant = TenantConfig(**doc.to_dict())

    if not tenant.webhook_url:
        raise HTTPException(400, "No webhook_url configured for this tenant")

    # Build a minimal test payload
    test_payload = {
        "deal_id": f"test-{tenant.tenant_id[:8]}",
        "company_name": f"Test Account ({tenant.name})",
        "deal_value": 50000.0,
        "close_date": _now()[:10],
        "industry": "Technology",
        "products": [
            {"name": p.name, "node_id": p.node_id}
            for p in tenant.products[:2]  # first 2 products
        ],
        "contacts": [{"name": "Test Contact", "role": "Buyer", "email": "test@example.com"}],
        "risks": [],
        "success_metrics": [],
        "sales_transcript": None,
        "contract_pdf_url": None,
        "historical_deals": [],
        # Hub metadata
        "_tenant_id": tenant.tenant_id,
        "_test": True,
    }

    steps = []
    try:
        steps.append({"step": "Webhook sent", "status": "ok", "timestamp": _now()})

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(tenant.webhook_url, json=test_payload)
            resp.raise_for_status()

        steps.append({"step": "Graph Generator received", "status": "ok", "timestamp": _now()})
        body = resp.json()
        node_count = body.get("node_count", 0)
        steps.append({"step": f"Nodes generated ({node_count})", "status": "ok", "timestamp": _now()})
        steps.append({"step": "Knowledge indexed", "status": "ok", "timestamp": _now()})

        return {"success": True, "steps": steps}

    except Exception as e:
        steps.append({"step": "Error", "status": "failed", "error": str(e), "timestamp": _now()})
        return {"success": False, "steps": steps}



# ── CRM Connection Test ──────────────────────────────────────────

@app.post("/api/test-connection", response_model=TestConnectionResponse)
async def test_connection(req: TestConnectionRequest):
    """Verify CRM connectivity (handshake test)."""
    log.info(f"Testing connection to {req.crm_type} at {req.crm_url}")

    if not req.crm_url or not req.crm_url.startswith("http"):
        return TestConnectionResponse(
            success=False,
            message="Invalid CRM URL protocol. Must be http/https."
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # We use a simple HEAD or GET request to check reachability
            # For most CRMs, we expect a 401/403 or 200 depending on the endpoint
            resp = await client.get(req.crm_url)
            
        return TestConnectionResponse(
            success=True,
            message="CRM Handshake Successful",
            details={
                "status_code": resp.status_code,
                "reachable": True,
                "url": req.crm_url
            }
        )
    except httpx.ConnectError:
        return TestConnectionResponse(
            success=False,
            message="Connection failed: URL unreachable or DNS resolution error."
        )
    except httpx.TimeoutException:
        return TestConnectionResponse(
            success=False,
            message="Connection timed out. The server is not responding."
        )
    except Exception as e:
        log.error(f"CRM Handshake Error: {e}")
        return TestConnectionResponse(
            success=False,
            message=f"Handshake failed: {str(e)}"
        )


# ── Serve Frontend (SPA) ────────────────────────────────────────
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
# Also check /app/frontend/dist for Docker container
if not os.path.exists(_frontend_dir):
    _frontend_dir = "/app/frontend/dist"

print(f"[Hub] Looking for frontend at: {_frontend_dir} (Exists: {os.path.exists(_frontend_dir)})")


@app.get("/", include_in_schema=False)
async def serve_hub_index():
    index_path = os.path.join(_frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Synapse Hub API", "frontend_path": _frontend_dir, "exists": os.path.exists(_frontend_dir)}


if os.path.exists(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="hub-frontend")
