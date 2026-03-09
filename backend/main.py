"""Synapse Backend Ã¢â‚¬â€ FastAPI Application Entry Point.

R2: Adds WebSocket endpoint for Gemini Live voice sessions, session management,
and real-time bidirectional audio streaming.
"""

from __future__ import annotations

import asyncio
import base64
import json
import uuid
from datetime import datetime

import httpx
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import os
import sys

# Add root directory to python path for shared modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import config
# Hub API URL
HUB_API_URL = os.getenv("HUB_API_URL", "http://localhost:8003")
from agent.synapse_agent import run_text_conversation
from live.session import LiveSession

app = FastAPI(
    title="Synapse API",
    description="Gemini Live voice agent for B2B SaaS customer success briefings",
    version="3.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from core.auth import verify_tenant_context, sign_tenant_context, DEMO_SECRET_KEY
import hmac

@app.middleware("http")
async def tenant_context_middleware(request: Request, call_next):
    """Enforce and propagate tenant context for all API requests.
    
    1. Extract from 'Authorization: Bearer <token>'
    2. Fallback to 'X-Tenant-Id' header (for backward compatibility/internal)
    3. Attach to request.state.tenant_id
    """
    # Oracle CLOSED logic: only base discovery is bypassed.
    # Individual lookups like /api/tenants/{id} or /api/resolve-tenant MUST be context-aware
    # (except for resolve-tenant which is the bootstrap point itself)
    bypass_paths = ["/health", "/api/tenants", "/api/resolve-tenant", "/api/webhooks", "/docs", "/openapi.json"]
    
    # Restrict /api/tenants bypass to ONLY the base GET listing (Picker)
    is_bypassed = (request.url.path == "/health") or \
                  (request.url.path == "/api/tenants" and request.method == "GET") or \
                  (request.url.path == "/api/resolve-tenant") or \
                  (request.url.path.startswith("/api/webhooks")) or \
                  (request.url.path in ["/docs", "/openapi.json"])
    
    tenant_id = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        tenant_id = verify_tenant_context(token)
    
    if not tenant_id:
        # Fallback to plain header if no token (for internal dev or legacy tools)
        tenant_id = request.headers.get("X-Tenant-Id")
        
    # Inject into request state
    request.state.tenant_id = tenant_id
    
    # Enforce policy: If not bypassed and no tenant_id, block it
    if not is_bypassed and not tenant_id:
        return JSONResponse(
            status_code=401,
            content={"error": "Tenant context required (X-Tenant-Id or Bearer token)"}
        )
        
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions to return standard JSON instead of crashing."""
    import traceback
    error_details = traceback.format_exc()
    print(f"[ERROR] Unhandled exception on {request.url.path}:\n{error_details}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "details": str(exc)},
    )

# Ã¢â€â‚¬Ã¢â€â‚¬ Active Session Objects (for WebSocket connections only) Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
# Note: Session metadata is persisted in Firestore. This dict holds
# active LiveSession objects that have open WebSocket connections.
active_sessions: dict[str, LiveSession] = {}


# Ã¢â€â‚¬Ã¢â€â‚¬ Health Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "0.5.0",
        "environment": config.environment,
        "active_sessions": len(active_sessions),
    }


# Ã¢â€â‚¬Ã¢â€â‚¬ Webhook: CRM Deal Closed Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬

@app.post("/api/webhooks/crm/deal-closed/{tenant_id}")
async def webhook_deal_closed(tenant_id: str, request: Request):
    """Receive webhook from CRM Simulator and forward to Graph Generator."""
    payload = await request.json()
    deal_id = payload.get("deal_id", "unknown")
    company = payload.get("company_name", "unknown")
    print(f"[WEBHOOK] Deal closed for tenant {tenant_id}: {deal_id} - {company}")

    generator_url = config.graph_generator_url
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Forward directly to the tenant-aware ingest endpoint
            ingest_url = f"{generator_url.rstrip('/')}/ingest/{tenant_id}"
            response = await client.post(ingest_url, json=payload)
            result = response.json()
            print(f"[WEBHOOK] Ingest triggered for tenant {tenant_id}: {result}")
            return JSONResponse(
                status_code=202,
                content={
                    "status": "generating",
                    "deal_id": deal_id,
                    "job_id": result.get("job_id"),
                    "message": f"Graph generation started for {company}",
                },
            )
    except Exception as e:
        print(f"[WEBHOOK] Failed to trigger graph generation: {e}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "received_but_generation_failed",
                "deal_id": deal_id,
                "error": str(e),
            },
        )


# —— Tenant Proxy (for Voice UI Tenant Picker + Role Selector) ——

from google.cloud import firestore as _firestore

_fs_client: _firestore.Client | None = None

def get_firestore_client() -> _firestore.Client:
    global _fs_client
    if _fs_client is None:
        _fs_client = _firestore.Client(project=config.project_id)
    return _fs_client


@app.get("/api/tenants")
async def list_tenants_for_voice_ui(request: Request):
    """List all tenants for the Voice UI Tenant Picker (Oracle closed)."""
    db = get_firestore_client()
    tenants = []
    docs = db.collection("tenants").stream()
    for doc in docs:
        data = doc.to_dict()
        tid = data.get("tenant_id", doc.id)
        
        # Oracle CLOSED. Tokens must be obtained via explicit login.
        # Only list public demo tenants for the picker
        if data.get("allow_public_demo") is not True:
            continue
            
        tenants.append({
            "tenant_id": tid,
            "name": data.get("name", "Unnamed"),
            "brand_name": data.get("brand_name", ""),
            "crm_type": data.get("crm", {}).get("crm_type", "custom"),
            "integration_status": data.get("integration_status", "not_configured"),
            "roles": data.get("agent", {}).get("roles", ["csm", "sales", "support"]),
            "product_count": len(data.get("products", [])),
            "synapse_tenant_token": None
        })
    return {"tenants": tenants, "count": len(tenants)}


@app.post("/api/tenants/{tenant_id}/login")
async def login_tenant_for_voice_ui(tenant_id: str):
    """Explicitly issue a signed token for a demo-enabled tenant (Voice UI)."""
    db = get_firestore_client()
    doc = db.collection("tenants").document(tenant_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    data = doc.to_dict()
    if data.get("allow_public_demo") is not True:
        raise HTTPException(status_code=403, detail="Public demo access disabled")
        
    token = sign_tenant_context(tenant_id)
    return {"synapse_tenant_token": token, "tenant_id": tenant_id}


@app.get("/api/resolve-tenant")
async def resolve_tenant_for_voice_ui(slug: str):
    """Resolve a tenant by its slug for Voice UI (Atlassian-style)."""
    db = get_firestore_client()
    docs = db.collection("tenants").where("slug", "==", slug).limit(1).stream()
    doc = next(docs, None)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Tenant '{slug}' not found")
    
    data = doc.to_dict()
    tid = data.get("tenant_id", doc.id)
    
    # Auto-issue token for public demo (only if enabled)
    token = None
    if data.get("allow_public_demo") is True:
        token = sign_tenant_context(tid)

    return {
        "tenant_id": tid,
        "name": data.get("name"),
        "brand_name": data.get("brand_name"),
        "synapse_tenant_token": token,
        "agent": data.get("agent"),
        "terminology_overrides": data.get("terminology_overrides")
    }


@app.get("/api/tenants/{tenant_id}")
async def get_tenant_for_voice_ui(tenant_id: str):
    """Get tenant config for Voice UI (roles, brand name, CRM type)."""
    db = get_firestore_client()
    doc = db.collection("tenants").document(tenant_id).get()
    if not doc.exists:
        return JSONResponse(status_code=404, content={"error": f"Tenant {tenant_id} not found"})
    data = doc.to_dict()
    return {
        "tenant_id": data.get("tenant_id", tenant_id),
        "name": data.get("name", "Unnamed"),
        "brand_name": data.get("brand_name", ""),
        "crm": data.get("crm", {}),
        "integration_status": data.get("integration_status", "not_configured"),
        "terminology_overrides": data.get("terminology_overrides", {}),
        "agent": data.get("agent", {}),
        "roles": data.get("agent", {}).get("roles", ["csm", "sales", "support"]),
        "products": [{"name": p.get("name"), "id": p.get("product_id")} for p in data.get("products", [])],
    }


# —— CRM Deal Proxy (for role-based dashboard) ————————————————————

@app.get("/api/crm/deals")
async def proxy_crm_deals(request: Request, tenant_id: str | None = None):
    """Serve deals from Firestore (tenant-aware).
    
    Enforces strict tenant isolation. Uses context if available.
    """
    ctx_tenant_id = request.state.tenant_id
    if tenant_id and ctx_tenant_id and tenant_id != ctx_tenant_id:
        return JSONResponse(status_code=403, content={"error": "Tenant mismatch"})
    
    effective_tenant_id = ctx_tenant_id or tenant_id
    if not effective_tenant_id:
         return JSONResponse(status_code=401, content={"error": "tenant_id required"})

    db = get_firestore_client()

    try:
        deals_ref = db.collection("deals").document(effective_tenant_id).collection("items")
        docs = deals_ref.stream()
        deals = []
        for doc in docs:
            deal = doc.to_dict()
            # Enrich with graph readiness from skill_graphs collection
            client_id = deal.get("client_id", "")
            if client_id:
                graph_doc = db.collection("skill_graphs").document(client_id).get()
                if graph_doc.exists:
                    data = graph_doc.to_dict()
                    # Strict tenant check on graph data
                    if data.get("tenant_id") == effective_tenant_id:
                        deal["graph_ready"] = data.get("status") == "ready"
                        deal["node_count"] = data.get("node_count", 0)
                    else:
                        deal["graph_ready"] = False
                        deal["node_count"] = 0
                else:
                    deal["graph_ready"] = False
                    deal["node_count"] = 0
            deals.append(deal)
        return {"deals": deals, "count": len(deals), "source": "firestore"}
    except Exception as e:
        print(f"[CRM_PROXY] Firestore deals query failed: {e}")
        return {"deals": [], "count": 0, "error": str(e)}

    # Fallback to CRM simulator removed for strict production fidelity
    # return {"deals": [], "count": 0, "error": "tenant_id required"}


# Ã¢â€â‚¬Ã¢â€â‚¬ Session Management Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬

class SessionStartRequest(BaseModel):
    client_id: str
    tenant_id: str | None = None # Optional in request, taken from context if missing
    csm_name: str = "CSM"
    deal_id: str | None = None
    role: str = "csm"


@app.post("/api/sessions/start")
async def start_session(req: SessionStartRequest, request: Request):
    """Create a new voice session, persist to Firestore, and return connection details."""
    # Enforce tenant context
    ctx_tenant_id = request.state.tenant_id
    if req.tenant_id and ctx_tenant_id and req.tenant_id != ctx_tenant_id:
        return JSONResponse(status_code=403, content={"error": "Tenant mismatch"})
    
    tenant_id = ctx_tenant_id or req.tenant_id
    if not tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})

    session_id = str(uuid.uuid4())[:8]

    # Load brand name from tenant config if provided
    brand_name = "ClawdView"
    db = get_firestore_client()
    doc = db.collection("tenants").document(tenant_id).get()
    if doc.exists:
        brand_name = doc.to_dict().get("brand_name", "ClawdView")

    session = LiveSession(
        session_id=session_id,
        client_id=req.client_id,
        tenant_id=req.tenant_id,
        brand_name=brand_name,
        csm_name=req.csm_name,
        deal_id=req.deal_id,
        role=req.role,
    )
    active_sessions[session_id] = session

    # Persist session creation to Firestore
    db = get_firestore_client()
    db.collection("sessions").document(session_id).set({
        "session_id": session_id,
        "client_id": req.client_id,
        "tenant_id": req.tenant_id,
        "brand_name": brand_name,
        "csm_name": req.csm_name,
        "deal_id": req.deal_id,
        "role": req.role,
        "started_at": session.started_at,
        "status": "active",
    })

    print(f"[SESSION] Created session {session_id} for tenant {req.tenant_id} and client {req.client_id}")

    return {
        "session_id": session_id,
        "websocket_url": f"/ws/sessions/{session_id}",
        "client_id": req.client_id,
        "csm_name": req.csm_name,
    }


@app.get("/api/sessions/{session_id}/history")
async def get_session_history(session_id: str, request: Request):
    """Get the transcript and traversal log for a session.

    Checks active in-memory sessions first.
    """
    ctx_tenant_id = request.state.tenant_id
    # Ironclad Oracle: Metadata isolation
    if not ctx_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required for history"})
        
    # Try active in-memory session
    session = active_sessions.get(session_id)
    if session:
        # Strict tenant verification
        if ctx_tenant_id and session.tenant_id != ctx_tenant_id:
            return JSONResponse(status_code=403, content={"error": "Access denied to session"})
        return session.get_history()

    # Fall back to Firestore
    # Note: LiveSession.get_history_from_firestore fetches context from the 'sessions' collection
    history = await LiveSession.get_history_from_firestore(session_id)
    if history:
        # Strict tenant verification for historical data
        if ctx_tenant_id and history.get("tenant_id") != ctx_tenant_id:
            return JSONResponse(status_code=403, content={"error": "Access denied to historical session"})
        return history

    return JSONResponse(status_code=404, content={"error": "Session not found"})


@app.get("/api/sessions")
async def list_sessions(request: Request):
    """List all sessions from Firestore (active and completed)."""
    from google.cloud import firestore
    db = get_firestore_client()

    # Only show sessions for the current tenant context
    ctx_tenant_id = request.state.tenant_id
    query = db.collection("sessions")
    
    if ctx_tenant_id:
        query = query.where("tenant_id", "==", ctx_tenant_id)
        
    docs = query.order_by(
        "started_at", direction=firestore.Query.DESCENDING
    ).limit(50).stream()

    sessions_list = []
    for doc in docs:
        data = doc.to_dict()
        sessions_list.append({
            "session_id": data.get("session_id", doc.id),
            "client_id": data.get("client_id"),
            "csm_name": data.get("csm_name"),
            "started_at": data.get("started_at"),
            "status": data.get("status", "unknown"),
            "total_tool_calls": data.get("total_tool_calls", 0),
            "total_messages": data.get("total_messages", 0),
        })

    return {"sessions": sessions_list, "count": len(sessions_list)}


# Ã¢â€â‚¬Ã¢â€â‚¬ WebSocket: Gemini Live Voice Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬

@app.websocket("/ws/sessions/{session_id}")
async def websocket_voice_session(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time voice conversations.

    Protocol:
    - Client sends: {"type": "audio", "data": "<base64 PCM 16kHz>"}
    - Client sends: {"type": "image", "data": "<base64 JPEG>"}
    - Client sends: {"type": "text", "text": "...", "end_of_turn": true}
    - Server sends: {"type": "audio", "data": "<base64 PCM 24kHz>"}
    - Server sends: {"type": "text", "text": "..."}
    - Server sends: {"type": "tool_call", "name": "...", "args": {...}}
    - Server sends: {"type": "turn_complete"}
    - Server sends: {"type": "interrupted"}
    """
    session = active_sessions.get(session_id)
    if not session:
        # Check Firestore if a different Cloud Run instance created it
        doc = get_firestore_client().collection("sessions").document(session_id).get()
        if doc.exists:
            data = doc.to_dict()
            session = LiveSession(
                session_id=session_id,
                client_id=data.get("client_id", "unknown"),
                tenant_id=data.get("tenant_id"),
                csm_name=data.get("csm_name", "CSM"),
                deal_id=data.get("deal_id"),
                role=data.get("role", "csm"),
            )
            active_sessions[session_id] = session
        else:
            await websocket.close(code=4004, reason="Session not found")
            return

    await websocket.accept()
    print(f"[WS] Client connected to session {session_id}")

    try:
        # Connect to Gemini Live API
        await session.connect()

        # Start receiving responses from Gemini Live (runs concurrently)
        async def forward_responses():
            """Forward Gemini Live responses to the WebSocket client."""
            async for event in session.receive_responses():
                try:
                    await websocket.send_json(event)
                except WebSocketDisconnect:
                    break

        response_task = asyncio.create_task(forward_responses())

        # Receive audio/text from the WebSocket client
        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type")

                if msg_type == "audio":
                    # Decode base64 audio and forward to Gemini Live
                    audio_bytes = base64.b64decode(data["data"])
                    await session.send_audio(audio_bytes)

                elif msg_type == "image":
                    # Decode base64 image and forward to Gemini Live Vision
                    image_bytes = base64.b64decode(data["data"])
                    await session.send_image(image_bytes)

                elif msg_type == "text":
                    # Text message natively supported by gemini-2.0-flash
                    await session.send_text(data.get("text", ""))

                elif msg_type == "end":
                    # Client requested end of session
                    break

        except WebSocketDisconnect:
            print(f"[WS] Client disconnected from session {session_id}")

        # Cancel the response forwarding task
        response_task.cancel()
        try:
            await response_task
        except asyncio.CancelledError:
            pass

    except Exception as e:
        print(f"[WS] Session {session_id} error: {e}")
        try:
            await websocket.send_json({"type": "error", "error": str(e)})
        except Exception:
            pass

    finally:
        await session.disconnect()
        print(f"[WS] Session {session_id} ended. "
              f"Tool calls: {len(session.tool_calls)}, "
              f"Nodes visited: {len(set(session.nodes_visited))}")


# Ã¢â€â‚¬Ã¢â€â‚¬ Text Conversation (from R1) Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬

class TextMessage(BaseModel):
    client_id: str
    message: str
    history: list[dict] | None = None


@app.post("/api/sessions/text")
async def text_conversation(req: TextMessage):
    """Have a text conversation with the Synapse agent (R1 endpoint, still available)."""
    print(f"[TEXT] Client: {req.client_id} | Message: {req.message}")

    # For text mode, we might need a tenant_id too if we want dynamic branding
    # For now, we'll try to find an active session or just use default
    brand_name = "ClawdView"
    
    result = await run_text_conversation(
        client_id=req.client_id,
        message=req.message,
        history=req.history,
        brand_name=brand_name
    )

    print(f"[TEXT] Tools used: {len(result['tool_calls'])} | "
          f"Nodes visited: {result['nodes_visited']}")
    return result


# Ã¢â€â‚¬Ã¢â€â‚¬ Client & Graph Status Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬

@app.get("/api/clients")
async def list_clients(request: Request, tenant_id: str | None = None):
    """List all client accounts for a specific tenant.
    
    Enforces strict tenant isolation.
    """
    ctx_tenant_id = request.state.tenant_id
    if tenant_id and ctx_tenant_id and tenant_id != ctx_tenant_id:
        return JSONResponse(status_code=403, content={"error": "Tenant mismatch"})
        
    effective_tenant_id = ctx_tenant_id or tenant_id
    if not effective_tenant_id:
         return JSONResponse(status_code=401, content={"error": "tenant_id required"})

    db = get_firestore_client()

    clients = []
    # Strictly require tenant_id for isolation
    docs = db.collection("skill_graphs").where("tenant_id", "==", effective_tenant_id).stream()

    for doc in docs:
        data = doc.to_dict()
        if data.get("status"):
            clients.append({
                "client_id": data.get("client_id", doc.id),
                "company_name": data.get("company_name", "Unknown Company"),
                "deal_id": data.get("deal_id"),
                "deal_value": data.get("deal_value", 0),
                "kickoff_date": data.get("kickoff_date", ""),
                "status": data.get("status", "unknown"),
                "node_count": data.get("node_count", 0),
                "generated_at": data.get("generated_at"),
            })

    return {"clients": clients, "count": len(clients), "tenant_id": tenant_id}


@app.get("/api/clients/{client_id}/graph/status")
async def get_graph_status(client_id: str):
    """Check if a client's knowledge graph is ready (supports both structured and legacy)."""
    db = get_firestore_client()

    # Check structured graph first
    kg_doc = db.collection("knowledge_graphs").document(client_id).get()
    if kg_doc.exists:
        data = kg_doc.to_dict()
        return {
            "client_id": client_id,
            "status": data.get("status", "unknown"),
            "graph_format": data.get("graph_format", "structured"),
            "entity_count": data.get("entity_count", 0),
            "edge_count": data.get("edge_count", 0),
            "entity_types": data.get("entity_types", []),
            "generated_at": data.get("generated_at"),
        }

    # Fall back to legacy skill_graphs
    doc = db.collection("skill_graphs").document(client_id).get()
    if not doc.exists:
        return {"client_id": client_id, "status": "not_found"}

    data = doc.to_dict()
    return {
        "client_id": client_id,
        "status": data.get("status", "unknown"),
        "graph_format": data.get("graph_format", "markdown"),
        "node_count": data.get("node_count", 0),
        "node_ids": data.get("node_ids", []),
        "generated_at": data.get("generated_at"),
    }


@app.get("/api/clients/{client_id}/graph/nodes")
async def list_graph_nodes(client_id: str, request: Request, tenant_id: str | None = None):
    """List all nodes in a client's skill graph with full metadata."""
    from core.storage import list_client_nodes
    from graph.traversal import follow_link
    
    effective_tenant_id = request.state.tenant_id or tenant_id
    if not effective_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})
        
    from graph.traversal import _verify_tenant_access
    _verify_tenant_access(effective_tenant_id, client_id)

    # Validation
    node_ids = list_client_nodes(client_id)
    nodes_metadata = []
    
    for nid in node_ids:
        data = follow_link(effective_tenant_id, client_id, nid)
        if "error" not in data:
            nodes_metadata.append({
                "node_id": nid,
                "title": data.get("title"),
                "layer": data.get("layer"),
                "links": data.get("links", []),
                "description": data.get("description", "")
            })
            
    return {
        "client_id": client_id, 
        "nodes": nodes_metadata, 
        "count": len(nodes_metadata)
    }


@app.get("/api/clients/{client_id}/graph/nodes/{node_id}")
async def read_graph_node(client_id: str, node_id: str, request: Request, tenant_id: str | None = None):
    """Read a specific node from a client's skill graph."""
    from core.storage import read_node
    from graph.traversal import _verify_tenant_access

    effective_tenant_id = request.state.tenant_id or tenant_id
    if not effective_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})
        
    _verify_tenant_access(effective_tenant_id, client_id)

    content = read_node(client_id, node_id)
    if not content:
        return JSONResponse(status_code=404, content={"error": f"Node {node_id} not found"})
    return {"client_id": client_id, "node_id": node_id, "content": content}


@app.get("/api/clients/{client_id}/graph/entities")
async def list_graph_entities(client_id: str, request: Request, tenant_id: str | None = None):
    """List all entities and edges in a client's structured knowledge graph."""
    from graph.traversal import _verify_tenant_access
    
    effective_tenant_id = request.state.tenant_id or tenant_id
    if not effective_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})
        
    _verify_tenant_access(effective_tenant_id, client_id)
    
    db = get_firestore_client()

    # Get all entities (without embeddings to keep payload small)
    entities = []
    entities_ref = db.collection("knowledge_graphs").document(client_id).collection("entities")
    for doc in entities_ref.stream():
        data = doc.to_dict()
        data.pop("embedding", None)
        data.pop("indexed_at", None)
        entities.append(data)

    # Get all edges
    edges = []
    edges_ref = db.collection("knowledge_graphs").document(client_id).collection("edges")
    for doc in edges_ref.stream():
        data = doc.to_dict()
        data.pop("indexed_at", None)
        edges.append(data)

    return {
        "client_id": client_id,
        "entities": entities,
        "edges": edges,
        "entity_count": len(entities),
        "edge_count": len(edges),
    }


# ── Agent Generative Outputs ─────────────────────────────────────

@app.post("/api/clients/{client_id}/outputs/briefing")
async def create_briefing(client_id: str, request: Request, tenant_id: str | None = None):
    """Generate a pre-meeting briefing summary from the knowledge graph."""
    from graph.outputs import generate_briefing
    
    effective_tenant_id = request.state.tenant_id or tenant_id
    if not effective_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})
        
    body = await request.json() if await request.body() else {}
    result = await generate_briefing(effective_tenant_id, client_id, csm_name=body.get("csm_name", "CSM"))
    return result


@app.post("/api/clients/{client_id}/outputs/action-plan")
async def create_action_plan(client_id: str, request: Request, tenant_id: str | None = None):
    """Generate a post-session action plan."""
    from graph.outputs import generate_action_plan
    
    effective_tenant_id = request.state.tenant_id or tenant_id
    if not effective_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})
        
    body = await request.json() if await request.body() else {}
    result = await generate_action_plan(effective_tenant_id, client_id, meeting_notes=body.get("meeting_notes"))
    return result


@app.post("/api/clients/{client_id}/outputs/risk-report")
async def create_risk_report(client_id: str, request: Request, tenant_id: str | None = None):
    """Generate a comprehensive risk assessment report."""
    from graph.outputs import generate_risk_report
    
    effective_tenant_id = request.state.tenant_id or tenant_id
    if not effective_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})
        
    result = await generate_risk_report(effective_tenant_id, client_id)
    return result


@app.post("/api/clients/{client_id}/outputs/recommendations")
async def create_recommendations(client_id: str, request: Request, tenant_id: str | None = None):
    """Generate strategic recommendations."""
    from graph.outputs import generate_recommendations
    
    effective_tenant_id = request.state.tenant_id or tenant_id
    if not effective_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})
        
    body = await request.json() if await request.body() else {}
    result = await generate_recommendations(effective_tenant_id, client_id, focus=body.get("focus", "general"))
    return result


@app.post("/api/clients/{client_id}/outputs/handoff")
async def create_handoff(client_id: str, request: Request, tenant_id: str | None = None):
    """Generate a team handoff document."""
    from graph.outputs import generate_handoff
    
    effective_tenant_id = request.state.tenant_id or tenant_id
    if not effective_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})
        
    body = await request.json()
    result = await generate_handoff(
        effective_tenant_id,
        client_id,
        from_team=body.get("from_team", "Sales"),
        to_team=body.get("to_team", "Customer Success"),
    )
    return result


@app.post("/api/clients/{client_id}/outputs/transcript")
async def create_transcript(client_id: str, request: Request, tenant_id: str | None = None):
    """Generate a role-based transcript/script from the knowledge graph."""
    from graph.outputs import generate_transcript
    
    effective_tenant_id = request.state.tenant_id or tenant_id
    if not effective_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})
        
    body = await request.json()
    result = await generate_transcript(
        effective_tenant_id,
        client_id,
        transcript_type=body.get("transcript_type", "sales_script"),
        user_role=body.get("user_role"),
        additional_context=body.get("additional_context"),
    )
    return result


@app.get("/api/clients/{client_id}/outputs/transcript-types")
async def list_transcript_types(client_id: str):
    """List available transcript types."""
    from graph.outputs import TRANSCRIPT_TYPES
    return {
        "types": [
            {"id": k, "title": v["title"]}
            for k, v in TRANSCRIPT_TYPES.items()
        ]
    }


@app.get("/api/clients/{client_id}/outputs")
async def list_client_outputs(client_id: str, request: Request, tenant_id: str | None = None):
    """List all generated outputs for a client."""
    from graph.outputs import list_outputs
    
    effective_tenant_id = request.state.tenant_id or tenant_id
    if not effective_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})
        
    outputs = await list_outputs(effective_tenant_id, client_id)
    return {"client_id": client_id, "outputs": outputs, "count": len(outputs)}


@app.get("/api/clients/{client_id}/outputs/{output_id}")
async def get_client_output(client_id: str, output_id: str, request: Request, tenant_id: str | None = None):
    """Retrieve a specific generated output."""
    from graph.outputs import get_output
    
    effective_tenant_id = request.state.tenant_id or tenant_id
    if not effective_tenant_id:
        return JSONResponse(status_code=401, content={"error": "Tenant context required"})
        
    result = await get_output(effective_tenant_id, client_id, output_id)
    if not result:
        return JSONResponse(status_code=404, content={"error": f"Output {output_id} not found"})
    return result










