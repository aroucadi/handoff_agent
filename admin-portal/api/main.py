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

SYNAPSE_ADMIN_KEY = os.getenv("SYNAPSE_ADMIN_KEY")
if not SYNAPSE_ADMIN_KEY:
    raise RuntimeError("Critical Security Configuration Missing: SYNAPSE_ADMIN_KEY environment variable is required.")
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
        "status": "configuring",
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
_frontend_dir = None
_candidates = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist"),
    "/app/frontend/dist",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist"),
]
for _c in _candidates:
    if os.path.isdir(_c):
        _frontend_dir = _c
        break
if not _frontend_dir:
    _frontend_dir = "/app/frontend/dist"

print(f"[Admin] Frontend dir: {_frontend_dir} (Exists: {os.path.isdir(_frontend_dir)})")
if os.path.isdir(_frontend_dir):
    _assets = os.path.join(_frontend_dir, "assets")
    if os.path.isdir(_assets):
        print(f"[Admin] Assets: {os.listdir(_assets)}")


@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    """SPA catch-all: serve static files if they exist, otherwise index.html."""
    file_path = os.path.join(_frontend_dir, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(_frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "Not Found"}
