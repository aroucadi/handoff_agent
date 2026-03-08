import os
from fastapi import FastAPI, HTTPException, Header, Depends
from google.cloud import firestore
import uuid
import hmac
from typing import Optional, List
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Synapse Admin API")

SYNAPSE_ADMIN_KEY = os.getenv("SYNAPSE_ADMIN_KEY", "synapse-admin-demo-key-2026")
db = firestore.Client()
TENANTS_COLLECTION = "tenants"

class TenantCreate(BaseModel):
    name: str
    brand_name: str
    crm_type: str = "custom"
    tenant_id: Optional[str] = None
    slug: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok", "service": "synapse-admin-api"}

def verify_admin_key(x_synapse_admin_key: str = Header(...)):
    if not hmac.compare_digest(x_synapse_admin_key, SYNAPSE_ADMIN_KEY):
        raise HTTPException(status_code=401, detail="Invalid Admin Key")
    return x_synapse_admin_key

@app.get("/api/tenants")
async def list_tenants(admin_key: str = Depends(verify_admin_key)):
    tenants = []
    docs = db.collection(TENANTS_COLLECTION).stream()
    for doc in docs:
        data = doc.to_dict()
        # Filter sensitive fields if necessary, but this is the Admin portal
        tenants.append(data)
    return {"tenants": tenants}

@app.post("/api/tenants", status_code=201)
async def create_tenant(tenant: TenantCreate, admin_key: str = Depends(verify_admin_key)):
    tenant_id = tenant.tenant_id or str(uuid.uuid4())[:8]
    slug = tenant.slug or tenant.name.lower().replace(" ", "-")
    
    # Ensure slug uniqueness
    existing_slugs = db.collection(TENANTS_COLLECTION).where("slug", "==", slug).limit(1).get()
    if existing_slugs:
        slug = f"{slug}-{str(uuid.uuid4())[:4]}"

    tenant_data = {
        "tenant_id": tenant_id,
        "slug": slug,
        "name": tenant.name,
        "brand_name": tenant.brand_name,
        "crm_type": tenant.crm_type,
        "status": "provisioned",
        "crm": {
            "crm_type": tenant.crm_type,
            "connected": False
        },
        "agent": {
            "brand_name": tenant.brand_name,
            "roles": [],
            "persona": f"Proactive assistant for {tenant.name}."
        }
    }
    
    db.collection(TENANTS_COLLECTION).document(tenant_id).set(tenant_data)
    return tenant_data

@app.delete("/api/tenants/{tenant_id}")
async def delete_tenant(tenant_id: str, admin_key: str = Depends(verify_admin_key)):
    db.collection(TENANTS_COLLECTION).document(tenant_id).delete()
    return {"message": f"Tenant {tenant_id} deleted"}

# ── Serve Frontend (SPA) ────────────────────────────────────────
_frontend_dir = os.path.join(os.path.dirname(__file__), "..", "dist")
# Also check /app/frontend/dist for Docker container parity
if not os.path.exists(_frontend_dir):
    _frontend_dir = "/app/frontend/dist"

@app.get("/", include_in_schema=False)
async def serve_admin_index():
    index_path = os.path.join(_frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Synapse Admin API", "frontend_path": _frontend_dir, "exists": os.path.exists(_frontend_dir)}

if os.path.exists(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="admin-frontend")
