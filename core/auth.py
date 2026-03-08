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
    DEMO_SECRET_KEY = "synapse-demo-secret-2026"
    log.warning("DEMO_SECRET_KEY not set. Using stable demo fallback. This is for investor discovery only.")
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

import os # Added import for DEMO_SECRET_KEY
