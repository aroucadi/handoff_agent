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

@app.post("/api/webhooks/crm/deal-closed")
async def webhook_deal_closed(request: Request):
    """Receive webhook from CRM Simulator and forward to Graph Generator."""
    payload = await request.json()
    deal_id = payload.get("deal_id", "unknown")
    company = payload.get("company_name", "unknown")
    print(f"[WEBHOOK] Deal closed: {deal_id} Ã¢â‚¬â€ {company}")

    generator_url = config.graph_generator_url
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(generator_url, json=payload)
            result = response.json()
            print(f"[WEBHOOK] Graph generation triggered: {result}")
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
async def list_tenants_for_voice_ui():
    """List all tenants for the Voice UI Tenant Picker.

    In production this would be scoped to the authenticated user's org.
    For demo purposes, returns all tenants from the Hub's Firestore collection.
    """
    db = get_firestore_client()
    tenants = []
    docs = db.collection("tenants").stream()
    for doc in docs:
        data = doc.to_dict()
        tenants.append({
            "tenant_id": data.get("tenant_id", doc.id),
            "name": data.get("name", "Unnamed"),
            "brand_name": data.get("brand_name", ""),
            "crm_type": data.get("crm", {}).get("crm_type", "custom"),
            "integration_status": data.get("integration_status", "not_configured"),
            "roles": data.get("agent", {}).get("roles", ["csm", "sales", "support"]),
            "product_count": len(data.get("products", [])),
        })
    return {"tenants": tenants, "count": len(tenants)}


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
        "crm_type": data.get("crm", {}).get("crm_type", "custom"),
        "integration_status": data.get("integration_status", "not_configured"),
        "roles": data.get("agent", {}).get("roles", ["csm", "sales", "support"]),
        "products": [{"name": p.get("name"), "id": p.get("product_id")} for p in data.get("products", [])],
    }


# —— CRM Deal Proxy (for role-based dashboard) ————————————————————

@app.get("/api/crm/deals")
async def proxy_crm_deals(tenant_id: str = None):
    """Serve deals from Firestore (tenant-aware) or CRM simulator (fallback).

    In real-life mode, deals are populated by the Graph Generator's ingest
    endpoint when CRM webhooks fire. The Voice UI dashboard reads from here.
    """
    db = get_firestore_client()

    # ── Tenant-aware mode: read from Firestore ──
    if tenant_id:
        try:
            deals_ref = db.collection("deals").document(tenant_id).collection("items")
            docs = deals_ref.stream()
            deals = []
            for doc in docs:
                deal = doc.to_dict()
                # Enrich with graph readiness from skill_graphs collection
                client_id = deal.get("client_id", "")
                if client_id:
                    graph_doc = db.collection("skill_graphs").document(client_id).get()
                    deal["graph_ready"] = (
                        graph_doc.exists
                        and graph_doc.to_dict().get("status") == "ready"
                    ) if graph_doc.exists else False
                    deal["node_count"] = graph_doc.to_dict().get("node_count", 0) if graph_doc.exists else 0
                deals.append(deal)
            return {"deals": deals, "count": len(deals), "source": "firestore"}
        except Exception as e:
            print(f"[CRM_PROXY] Firestore deals query failed: {e}")
            return {"deals": [], "count": 0, "error": str(e)}

    # ── Fallback: read from CRM simulator (backward compatible) ──
    crm_url = config.crm_simulator_url.rstrip("/") + "/api/deals"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(crm_url)
            crm_data = response.json()
    except Exception as e:
        print(f"[CRM_PROXY] Failed to fetch deals: {e}")
        return {"deals": [], "count": 0, "error": str(e)}

    # Enrich each deal with graph readiness
    deals = crm_data.get("deals", [])
    for deal in deals:
        company_name = deal.get("company_name", "")
        client_id = company_name.lower().replace(" ", "-").replace(",", "").replace(".", "")
        doc = db.collection("skill_graphs").document(client_id).get()
        deal["client_id"] = client_id
        deal["graph_ready"] = doc.exists and doc.to_dict().get("status") == "ready" if doc.exists else False
        deal["node_count"] = doc.to_dict().get("node_count", 0) if doc.exists else 0

    return {"deals": deals, "count": len(deals), "source": "simulator"}


# Ã¢â€â‚¬Ã¢â€â‚¬ Session Management Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬

class SessionStartRequest(BaseModel):
    client_id: str
    tenant_id: str | None = None # Required for dynamic branding
    csm_name: str = "CSM"
    deal_id: str | None = None
    role: str = "csm"


@app.post("/api/sessions/start")
async def start_session(req: SessionStartRequest):
    """Create a new voice session, persist to Firestore, and return connection details."""
    session_id = str(uuid.uuid4())[:8]

    # Load brand name from tenant config if provided
    brand_name = "ClawdView"
    if req.tenant_id:
        db = get_firestore_client()
        doc = db.collection("tenants").document(req.tenant_id).get()
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
async def get_session_history(session_id: str):
    """Get the transcript and traversal log for a session.

    Checks active in-memory sessions first, then falls back to Firestore.
    """
    # Try active in-memory session
    session = active_sessions.get(session_id)
    if session:
        return session.get_history()

    # Fall back to Firestore
    history = await LiveSession.get_history_from_firestore(session_id)
    if history:
        return history

    return JSONResponse(status_code=404, content={"error": "Session not found"})


@app.get("/api/sessions")
async def list_sessions():
    """List all sessions from Firestore (active and completed)."""
    from google.cloud import firestore
    db = get_firestore_client()

    sessions_list = []
    docs = db.collection("sessions").order_by(
        "started_at", direction=firestore.Query.DESCENDING
    ).limit(50).stream()

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
async def list_clients(tenant_id: str = None):
    """List all client accounts with graph status, optionally filtered by tenant."""
    db = get_firestore_client()

    clients = []
    # If tenant_id provided, filter the skill_graphs
    if tenant_id:
        # Use simple string prefix match or dedicated field
        # Since we added tenant_id field to skill_graphs doc, use that
        docs = db.collection("skill_graphs").where("tenant_id", "==", tenant_id).stream()
    else:
        docs = db.collection("skill_graphs").stream()

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
    """Check if a client's skill graph is ready."""
    db = get_firestore_client()

    doc = db.collection("skill_graphs").document(client_id).get()
    if not doc.exists:
        return {"client_id": client_id, "status": "not_found"}

    data = doc.to_dict()
    return {
        "client_id": client_id,
        "status": data.get("status", "unknown"),
        "node_count": data.get("node_count", 0),
        "node_ids": data.get("node_ids", []),
        "generated_at": data.get("generated_at"),
    }


@app.get("/api/clients/{client_id}/graph/nodes")
async def list_graph_nodes(client_id: str):
    """List all nodes in a client's skill graph with full metadata.
    
    This pre-fetches the links and layers so the UI can draw a connected graph.
    """
    from core.storage import list_client_nodes
    from graph.traversal import follow_link
    
    node_ids = list_client_nodes(client_id)
    nodes_metadata = []
    
    for nid in node_ids:
        # fetch basic metadata (links/layer) without full body content to keep payload small
        # reuse follow_link logic for consistency
        data = follow_link(client_id, nid)
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
async def read_graph_node(client_id: str, node_id: str):
    """Read a specific node from a client's skill graph."""
    from core.storage import read_node
    content = read_node(client_id, node_id)
    if not content:
        return JSONResponse(status_code=404, content={"error": f"Node {node_id} not found"})
    return {"client_id": client_id, "node_id": node_id, "content": content}
