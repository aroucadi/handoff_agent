"""Handoff Backend — FastAPI Application Entry Point.

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

from config import config
from agent.handoff_agent import run_text_conversation
from live.session import LiveSession

app = FastAPI(
    title="Handoff API",
    description="Gemini Live voice agent for B2B SaaS customer success handoffs",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Active Session Objects (for WebSocket connections only) ────
# Note: Session metadata is persisted in Firestore. This dict holds
# active LiveSession objects that have open WebSocket connections.
active_sessions: dict[str, LiveSession] = {}


# ── Health ──────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "0.5.0",
        "environment": config.environment,
        "active_sessions": len(active_sessions),
    }


# ── Webhook: CRM Deal Closed ───────────────────────────────────

@app.post("/api/webhooks/crm/deal-closed")
async def webhook_deal_closed(request: Request):
    """Receive webhook from CRM Simulator and forward to Graph Generator."""
    payload = await request.json()
    deal_id = payload.get("deal_id", "unknown")
    company = payload.get("company_name", "unknown")
    print(f"[WEBHOOK] Deal closed: {deal_id} — {company}")

    generator_url = "http://localhost:8002/generate"
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


# ── Session Management ─────────────────────────────────────────

class SessionStartRequest(BaseModel):
    client_id: str
    csm_name: str = "CSM"


@app.post("/api/sessions/start")
async def start_session(req: SessionStartRequest):
    """Create a new voice session, persist to Firestore, and return connection details."""
    session_id = str(uuid.uuid4())[:8]

    session = LiveSession(
        session_id=session_id,
        client_id=req.client_id,
        csm_name=req.csm_name,
    )
    active_sessions[session_id] = session

    # Persist session creation to Firestore
    from google.cloud import firestore
    db = firestore.Client(project=config.project_id)
    db.collection("sessions").document(session_id).set({
        "session_id": session_id,
        "client_id": req.client_id,
        "csm_name": req.csm_name,
        "started_at": session.started_at,
        "status": "active",
    })

    print(f"[SESSION] Created session {session_id} for client {req.client_id} (persisted to Firestore)")

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
    db = firestore.Client(project=config.project_id)

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


# ── WebSocket: Gemini Live Voice ────────────────────────────────

@app.websocket("/ws/sessions/{session_id}")
async def websocket_voice_session(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time voice conversations.

    Protocol:
    - Client sends: {"type": "audio", "data": "<base64 PCM 16kHz>"}
    - Client sends: {"type": "text", "text": "...", "end_of_turn": true}
    - Server sends: {"type": "audio", "data": "<base64 PCM 24kHz>"}
    - Server sends: {"type": "text", "text": "..."}
    - Server sends: {"type": "tool_call", "name": "...", "args": {...}}
    - Server sends: {"type": "turn_complete"}
    - Server sends: {"type": "interrupted"}
    """
    session = active_sessions.get(session_id)
    if not session:
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

                elif msg_type == "text":
                    # Text message (for testing or fallback)
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


# ── Text Conversation (from R1) ────────────────────────────────

class TextMessage(BaseModel):
    client_id: str
    message: str
    history: list[dict] | None = None


@app.post("/api/sessions/text")
async def text_conversation(msg: TextMessage):
    """Have a text conversation with the Handoff agent (R1 endpoint, still available)."""
    print(f"[TEXT] Client: {msg.client_id} | Message: {msg.message}")

    result = await run_text_conversation(
        client_id=msg.client_id,
        message=msg.message,
        history=msg.history,
    )

    print(f"[TEXT] Tools used: {len(result['tool_calls'])} | "
          f"Nodes visited: {result['nodes_visited']}")
    return result


# ── Client & Graph Status ──────────────────────────────────────

@app.get("/api/clients")
async def list_clients():
    """List all client accounts with graph status."""
    from google.cloud import firestore
    db = firestore.Client(project=config.project_id)

    clients = []
    docs = db.collection("skill_graphs").stream()
    for doc in docs:
        data = doc.to_dict()
        if data.get("status"):
            clients.append({
                "client_id": data.get("client_id", doc.id),
                "company_name": data.get("company_name", "Unknown Company"),
                "deal_value": data.get("deal_value", 0),
                "kickoff_date": data.get("kickoff_date", ""),
                "status": data.get("status", "unknown"),
                "node_count": data.get("node_count", 0),
                "generated_at": data.get("generated_at"),
            })

    return {"clients": clients, "count": len(clients)}


@app.get("/api/clients/{client_id}/graph/status")
async def get_graph_status(client_id: str):
    """Check if a client's skill graph is ready."""
    from google.cloud import firestore
    db = firestore.Client(project=config.project_id)

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
    """List all nodes in a client's skill graph."""
    from graph.storage import list_client_nodes
    nodes = list_client_nodes(client_id)
    return {"client_id": client_id, "nodes": nodes, "count": len(nodes)}


@app.get("/api/clients/{client_id}/graph/nodes/{node_id}")
async def read_graph_node(client_id: str, node_id: str):
    """Read a specific node from a client's skill graph."""
    from graph.storage import read_node
    content = read_node(client_id, node_id)
    if not content:
        return JSONResponse(status_code=404, content={"error": f"Node {node_id} not found"})
    return {"client_id": client_id, "node_id": node_id, "content": content}
