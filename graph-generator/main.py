"""Graph Generator — Main Orchestrator.

Receives a deal-closed webhook payload, orchestrates the full graph generation pipeline:
1. Extract entities from CRM data and transcript (Gemini 3.1 Pro)
2. Generate markdown skill graph nodes (Gemini 3.1 Pro)
3. Write nodes to GCS
4. Index nodes with embeddings in Firestore (gemini-embedding-001)
"""

from __future__ import annotations

import uuid
import traceback
from datetime import datetime

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import os
import sys

# Add root directory to python path for shared modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import config
from extractors.crm_extractor import extract_from_crm_payload
from extractors.transcript_extractor import extract_from_transcript
from extractors.contract_extractor import extract_from_contract
from node_generator import generate_client_nodes
from core.storage import write_all_nodes
from indexer import index_all_nodes, get_graph_status

app = FastAPI(
    title="Handoff Graph Generator",
    description="Generates client skill graphs from CRM data using Gemini 3.1 Pro",
    version="3.1.0",
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

# In-memory job tracking
jobs: dict[str, dict] = {}


@app.get("/health")
async def health():
    return {"status": "ok", "service": "graph-generator", "version": "0.2.0"}


async def _run_generation(job_id: str, payload: dict):
    """Background task that runs the full graph generation pipeline."""
    jobs[job_id]["status"] = "extracting"

    try:
        # Step 1: Extract from CRM payload
        print(f"[JOB {job_id}] Step 1: Extracting CRM data...")
        crm_data = extract_from_crm_payload(payload)

        client_id = payload.get("deal_id", "unknown").lower().replace(" ", "-")
        company_name = payload.get("company_name", "Unknown Company")
        industry = payload.get("industry", "general")

        # Step 2: Extract asynchronously (Transcript & Contract in parallel)
        print(f"[JOB {job_id}] Step 2: Running parallel AI extractions (Gemini 3.1 Pro)...")
        jobs[job_id]["status"] = "analyzing_documents"
        
        transcript = payload.get("sales_transcript")
        contract_pdf_url = payload.get("contract_pdf_url")
        
        async def safe_extract_transcript():
            if transcript and transcript.strip():
                print(f"[JOB {job_id}] Extracting from transcript...")
                return await extract_from_transcript(transcript)
            print(f"[JOB {job_id}] No transcript provided.")
            return None
            
        async def safe_extract_contract():
            if contract_pdf_url:
                print(f"[JOB {job_id}] Extracting from contract PDF...")
                return await extract_from_contract(client_id, contract_pdf_url)
            print(f"[JOB {job_id}] No contract PDF URL provided.")
            return None
            
        import asyncio
        transcript_data, contract_data = await asyncio.gather(
            safe_extract_transcript(),
            safe_extract_contract(),
        )
        
        if transcript_data:
            print(f"[JOB {job_id}] Transcript extraction complete: {len(transcript_data.get('stakeholders', []))} stakeholders")
        if contract_data:
            print(f"[JOB {job_id}] Contract extraction complete: {len(contract_data.get('contracted_modules', []))} modules")

        # Step 3: Generate nodes
        print(f"[JOB {job_id}] Step 3: Generating nodes (Multi-Agent: Generator + Reviewer) with Gemini 3.1 Pro...")
        jobs[job_id]["status"] = "generating_nodes"
        
        # This function now orchestrates both the Generation and Review passes internally
        nodes = await generate_client_nodes(
            client_id=client_id,
            company_name=company_name,
            industry=industry,
            crm_data=crm_data,
            transcript_data=transcript_data,
            contract_data=contract_data,
        )
        
        jobs[job_id]["status"] = "reviewing_nodes" # Set briefly before writing to GCS
        print(f"[JOB {job_id}] Generated and reviewed {len(nodes)} nodes")

        # Step 4: Write to GCS
        print(f"[JOB {job_id}] Step 4: Writing nodes to GCS...")
        jobs[job_id]["status"] = "writing_to_gcs"
        uris = await write_all_nodes(client_id, nodes)
        print(f"[JOB {job_id}] Written {len(uris)} files to GCS")

        # Step 5: Index with embeddings
        print(f"[JOB {job_id}] Step 5: Indexing nodes with embeddings (gemini-embedding-001)...")
        jobs[job_id]["status"] = "indexing"
        indexed = await index_all_nodes(client_id, nodes, payload=payload)
        print(f"[JOB {job_id}] Indexed {len(indexed)} nodes in Firestore")

        # Done!
        jobs[job_id].update({
            "status": "complete",
            "client_id": client_id,
            "node_count": len(nodes),
            "node_ids": [n.get("node_id") for n in nodes],
            "gcs_uris": uris,
            "completed_at": datetime.utcnow().isoformat(),
        })

        # Step 6: Notify CSM (Firestore document)
        from core.db import get_firestore_client
        db = get_firestore_client()
        db.collection("notifications").document(client_id).set({
            "client_id": client_id,
            "company_name": company_name,
            "status": "graph_ready",
            "node_count": len(nodes),
            "generated_at": datetime.utcnow().isoformat(),
            "csm_id": payload.get("csm_id", "unknown"),
            "deal_id": payload.get("deal_id", "unknown"),
        })

        print(f"[JOB {job_id}] ✅ Graph generation complete for {company_name}")

    except Exception as e:
        traceback.print_exc()
        jobs[job_id].update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat(),
        })
        print(f"[JOB {job_id}] ❌ Graph generation failed: {e}")


@app.post("/generate")
async def generate_graph(request: Request, background_tasks: BackgroundTasks):
    """Trigger graph generation for a closed deal.

    Accepts the same payload as the CRM webhook: deal_id, company_name, contacts, etc.
    Returns immediately with a job_id; generation runs in the background.
    """
    payload = await request.json()
    job_id = str(uuid.uuid4())[:8]

    company = payload.get("company_name", "unknown")
    print(f"[GENERATOR] Starting graph generation job {job_id} for {company}")

    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "company_name": company,
        "deal_id": payload.get("deal_id"),
        "started_at": datetime.utcnow().isoformat(),
    }

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
    """Check the status of a graph generation job."""
    job = jobs.get(job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": f"Job {job_id} not found"})
    return job


@app.get("/clients/{client_id}/status")
async def get_client_graph_status(client_id: str):
    """Check if a client's graph is ready (reads from Firestore)."""
    status = await get_graph_status(client_id)
    if not status:
        return {"client_id": client_id, "status": "not_found"}
    return status
