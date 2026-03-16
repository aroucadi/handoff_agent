import os
import hmac
import hashlib
import time
import base64
import json
from core.config import config

import logging
log = logging.getLogger("core.auth")

# A secret key for signing demo tokens.
# For the Investor Demo/Challenge submission, we use a stable default
# but log a warning if the secure environment variable is missing.
DEMO_SECRET_KEY = os.getenv("DEMO_SECRET_KEY")
if not DEMO_SECRET_KEY:
    # For local development without env vars, you might want a fallback, 
    # but for "Ironclad" mode we should enforce it or at least not use a known default in prod.
    raise RuntimeError("DEMO_SECRET_KEY environment variable is required for secure tenant isolation.")
else:
    log.info("DEMO_SECRET_KEY loaded from environment. Hardened context enabled.")

def sign_tenant_context(tenant_id: str, ttl: int = 86400) -> str:
    """Generate a signed demo token for a tenant ID.
    
    This is NOT a full JWT/Auth implementation, but a 'Signed Token' pattern
    to prove the request was tagged by a valid entry point (like the Hub or Selector).
    """
    expires_at = int(time.time()) + ttl
    payload = {
        "tenant_id": tenant_id,
        "exp": expires_at,
        "mode": "demo"
    }
    payload_json = json.dumps(payload, sort_keys=True)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip("=")
    
    signature = hmac.new(
        DEMO_SECRET_KEY.encode(),
        payload_b64.encode(),
        hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{payload_b64}.{sig_b64}"

def verify_tenant_context(token: str) -> str | None:
    """Verify a signed demo token and return the tenant_id if valid."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        
        payload_b64, sig_b64 = parts
        
        # Verify signature
        expected_sig = hmac.new(
            DEMO_SECRET_KEY.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).digest()
        actual_sig = base64.urlsafe_b64decode(sig_b64 + "==")
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        # Decode and check expiration
        missing_padding = len(payload_b64) % 4
        if missing_padding:
            payload_b64 += "=" * (4 - missing_padding)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        
        if payload.get("exp", 0) < time.time():
            return None
            
        return payload.get("tenant_id")
    except Exception as e:
        print(f"[AUTH] Token verification failed: {e}")
        return None


def verify_tenant_access(tenant_id: str, client_id: str) -> bool:
    """Authoritative tenant access verification.
    
    Checks if the given client_id belongs to the tenant_id by verifying
    the 'tenant_id' field on the graph status documents.
    
    Used by traversal and search modules to ensure strict data isolation.
    """
    if not tenant_id:
        return False
    
    # Fast path: deterministic prefix matches tenant
    if client_id.startswith(f"{tenant_id}_"):
        return True

    # Authoritative check from Firestore (for non-prefixed or legacy)
    from core.db import get_firestore_client
    db = get_firestore_client()
    
    # Check skill_graphs or knowledge_graphs status docs
    for coll in ["skill_graphs", "knowledge_graphs"]:
        doc = db.collection(coll).document(client_id).get()
        if doc.exists:
            stored_tenant = doc.to_dict().get("tenant_id")
            if stored_tenant == tenant_id:
                return True
            else:
                return False

    # Note: If no graph doc exists yet, we let it pass the isolation check 
    # but the subsequent read will naturally fail if the data isn't there.
    return client_id.startswith(f"{tenant_id}_")
