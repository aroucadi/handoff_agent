"""Graph Generator - Main Orchestrator.

Receives a deal-closed webhook payload, orchestrates the full graph generation pipeline.
Supports two output modes:
  - "structured" (Phase 1B): Ontology-driven entity+edge extraction
  - "markdown" (legacy): 8-node markdown document generation
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
from extractors.crm_extractor import extract_from_crm_payload, extract_entities_from_crm
from extractors.transcript_extractor import extract_from_transcript
from extractors.contract_extractor import extract_from_contract
from node_generator import generate_client_nodes, generate_structured_entities
from core.storage import write_all_nodes
from indexer import index_all_nodes, index_structured_graph, get_graph_status

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

# Mount the tenant-aware ingest endpoint
from ingest import router as ingest_router
app.include_router(ingest_router)

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
    return {"status": "ok", "service": "graph-generator", "version": "4.0.0"}


async def _run_generation(job_id: str, payload: dict):
    """Background task: runs the full graph generation pipeline.
    
    Branches between structured (entities+edges) and legacy (markdown) mode
    based on config.graph_output_format.
    """
    jobs[job_id]["status"] = "extracting"
    use_structured = config.graph_output_format == "structured"

    try:
        # Common: identifiers
        tenant_id = payload.get("_tenant_id", "default")
        company_name = payload.get("company_name", "Unknown Company")
        raw_client_id = company_name.lower().replace(" ", "-").replace(",", "").replace(".", "")
        client_id = f"{tenant_id}_{raw_client_id}"
        industry = payload.get("industry", "general")

        # Step 1: CRM Extraction
        mode_label = "structured" if use_structured else "legacy"
        print(f"[JOB {job_id}] Step 1: Extracting CRM data ({mode_label})...")
        if use_structured:
            crm_entities = extract_entities_from_crm(payload)
        else:
            crm_data = extract_from_crm_payload(payload)

        # Step 2: Parallel AI Extractions
        print(f"[JOB {job_id}] Step 2: Running parallel AI extractions...")
        jobs[job_id]["status"] = "analyzing_documents"
        transcript = payload.get("sales_transcript")
        contract_pdf_url = payload.get("contract_pdf_url")

        async def safe_extract_transcript():
            if transcript and transcript.strip():
                return await extract_from_transcript(transcript)
            return None

        async def safe_extract_contract():
            if contract_pdf_url:
                return await extract_from_contract(client_id, contract_pdf_url)
            return None

        import asyncio
        transcript_data, contract_data = await asyncio.gather(
            safe_extract_transcript(), safe_extract_contract(),
        )

        # Step 3+: Branch by output format
        if use_structured:
            print(f"[JOB {job_id}] Step 3: Extracting structured entities...")
            jobs[job_id]["status"] = "extracting_entities"
            graph_data = await generate_structured_entities(
                client_id=client_id, company_name=company_name, industry=industry,
                crm_entities=crm_entities, transcript_data=transcript_data,
                contract_data=contract_data, tenant_id=tenant_id,
            )
            e_count = len(graph_data.get("nodes", []))
            r_count = len(graph_data.get("edges", []))
            print(f"[JOB {job_id}] Extracted {e_count} entities, {r_count} edges")

            print(f"[JOB {job_id}] Step 4: Indexing structured graph...")
            jobs[job_id]["status"] = "indexing"
            status = await index_structured_graph(client_id, graph_data, payload=payload)

            jobs[job_id].update({
                "status": "complete", "client_id": client_id,
                "graph_format": "structured", "entity_count": e_count,
                "edge_count": r_count, "entity_types": status.get("entity_types", []),
                "completed_at": datetime.utcnow().isoformat(),
            })
        else:
            print(f"[JOB {job_id}] Step 3: Generating markdown nodes...")
            jobs[job_id]["status"] = "generating_nodes"
            nodes = await generate_client_nodes(
                client_id=client_id, company_name=company_name, industry=industry,
                crm_data=crm_data, transcript_data=transcript_data,
                contract_data=contract_data, tenant_id=tenant_id,
            )
            print(f"[JOB {job_id}] Generated {len(nodes)} nodes")

            jobs[job_id]["status"] = "writing_to_gcs"
            uris = await write_all_nodes(client_id, nodes)
            jobs[job_id]["status"] = "indexing"
            indexed = await index_all_nodes(client_id, nodes, payload=payload)

            jobs[job_id].update({
                "status": "complete", "client_id": client_id,
                "graph_format": "markdown", "node_count": len(nodes),
                "node_ids": [n.get("node_id") for n in nodes],
                "gcs_uris": uris, "completed_at": datetime.utcnow().isoformat(),
            })

        # Notify CSM
        from core.db import get_firestore_client
        db = get_firestore_client()
        db.collection("notifications").document(client_id).set({
            "client_id": client_id, "company_name": company_name,
            "status": "graph_ready",
            "graph_format": "structured" if use_structured else "markdown",
            "generated_at": datetime.utcnow().isoformat(),
            "csm_id": payload.get("csm_id", "unknown"),
            "deal_id": payload.get("deal_id", "unknown"),
        })
        print(f"[JOB {job_id}] Graph generation complete for {company_name}")

    except Exception as e:
        traceback.print_exc()
        jobs[job_id].update({
            "status": "failed", "error": str(e),
            "failed_at": datetime.utcnow().isoformat(),
        })
        print(f"[JOB {job_id}] Graph generation failed: {e}")


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
