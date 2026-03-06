"""Graph Generator - Main Orchestrator.

Receives a deal-closed webhook payload, orchestrates the full graph generation pipeline.
Supports two output modes:
  - "structured" (Phase 1B): Ontology-driven entity+edge extraction
  - "markdown" (legacy): 8-node markdown document generation
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import os
import sys

# Add root directory to python path for shared modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import config
from core.db import get_firestore_client
from orchestrator import _run_generation
from indexer import get_graph_status

app = FastAPI(
    title="Synapse Graph Generator",
    description="Generates client skill graphs from CRM data using Gemini",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
from ingest import router as ingest_router
app.include_router(ingest_router)

from sync_knowledge import router as sync_knowledge_router
app.include_router(sync_knowledge_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions."""
    import traceback
    error_details = traceback.format_exc()
    print(f"[ERROR] Unhandled exception on {request.url.path}:\n{error_details}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "details": str(exc)},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "graph-generator", "version": "4.0.0"}


@app.post("/generate")
async def generate_graph(request: Request, background_tasks: BackgroundTasks):
    """Trigger graph generation for a closed deal."""
    payload = await request.json()
    job_id = str(uuid.uuid4())[:8]

    company = payload.get("company_name", "unknown")
    print(f"[GENERATOR] Starting graph generation job {job_id} for {company}")

    # Write job to Firestore instead of memory
    db = get_firestore_client()
    db.collection("graph_jobs").document(job_id).set({
        "job_id": job_id,
        "status": "queued",
        "company_name": company,
        "deal_id": payload.get("deal_id"),
        "started_at": datetime.utcnow().isoformat(),
        "warnings": [],
    })

    background_tasks.add_task(_run_generation, job_id, payload)

    return JSONResponse(
        status_code=202,
        content={
            "job_id": job_id,
            "status": "queued",
            "message": f"Graph generation started for {company}",
        },
    )


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Check the status of a graph generation job in Firestore."""
    db = get_firestore_client()
    doc = db.collection("graph_jobs").document(job_id).get()
    if not doc.exists:
        return JSONResponse(status_code=404, content={"error": f"Job {job_id} not found"})
    return doc.to_dict()


@app.get("/clients/{client_id}/status")
async def get_client_graph_status(client_id: str):
    """Check if a client's graph is ready (reads from Firestore)."""
    status = await get_graph_status(client_id)
    if not status:
        return {"client_id": client_id, "status": "not_found"}
    return status

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
