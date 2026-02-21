"""Handoff Backend — FastAPI Application Entry Point.

R1: Adds text conversation endpoint, webhook-to-generator integration,
and client/graph status endpoints.
"""

from __future__ import annotations

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import config
from agent.handoff_agent import run_text_conversation

app = FastAPI(
    title="Handoff API",
    description="Gemini Live voice agent for B2B SaaS customer success handoffs",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ──────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.2.0", "environment": config.environment}


# ── Webhook: CRM Deal Closed ───────────────────────────────────

GRAPH_GENERATOR_URL = f"{config.crm_simulator_url.replace('8001', '8002')}"


@app.post("/api/webhooks/crm/deal-closed")
async def webhook_deal_closed(request: Request):
    """Receive webhook from CRM Simulator and forward to Graph Generator.

    In R1, this triggers real graph generation via the Graph Generator service.
    """
    payload = await request.json()
    deal_id = payload.get("deal_id", "unknown")
    company = payload.get("company_name", "unknown")
    print(f"[WEBHOOK] Deal closed: {deal_id} — {company}")

    # Forward to Graph Generator service
    generator_url = f"http://localhost:8002/generate"
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
                "message": "Webhook received but graph generator is not running. Start it with: cd graph-generator && uvicorn main:app --port 8002",
            },
        )


# ── Text Conversation ──────────────────────────────────────────

class TextMessage(BaseModel):
    client_id: str
    message: str
    history: list[dict] | None = None


@app.post("/api/sessions/text")
async def text_conversation(msg: TextMessage):
    """Have a text conversation with the Handoff agent.

    The agent navigates the client's skill graph to provide grounded answers.
    This is the R1 text-mode interface; voice comes in R2.
    """
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
        if data.get("status"):  # Only client-level status docs
            clients.append({
                "client_id": data.get("client_id", doc.id),
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
