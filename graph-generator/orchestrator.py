"""Graph Generator — Job Orchestrator.

Decouples the generation logic from the FastAPI entrypoints to resolve
circular dependencies between main.py and ingest.py.
"""

from __future__ import annotations

import os
import sys
import traceback
import asyncio
from datetime import datetime

from core.db import get_firestore_client
from google.cloud import firestore

# Global semaphore to bottleneck concurrent massive extraction prompts across background jobs
EXTRACTION_SEMAPHORE = asyncio.Semaphore(2)

def _update_job(job_id: str, updates: dict):
    db = get_firestore_client()
    db.collection("graph_jobs").document(job_id).update(updates)

def _add_job_warning(job_id: str, warning: str):
    db = get_firestore_client()
    db.collection("graph_jobs").document(job_id).update({
        "warnings": firestore.ArrayUnion([warning])
    })

async def _run_generation(job_id: str, payload: dict):
    """Background task: runs the full graph generation pipeline."""
    # This requires imports that might be in the parent dir
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    from core.config import config
    from core.db import get_firestore_client
    from extractors.crm_extractor import extract_from_crm_payload, extract_entities_from_crm
    from extractors.transcript_extractor import extract_from_transcript
    from extractors.contract_extractor import extract_from_contract
    from node_generator import generate_client_nodes, generate_structured_entities
    from core.storage import write_all_nodes
    from indexer import index_all_nodes, index_structured_graph, get_graph_status

    _update_job(job_id, {"status": "extracting"})
    use_structured = config.graph_output_format == "structured"

    try:
        # Common: identifiers
        tenant_id = payload.get("_tenant_id", "default")
        company_name = payload.get("company_name", "Unknown Company")
        industry = payload.get("industry", "general")

        # Step 1: CRM Extraction
        mode_label = "structured" if use_structured else "legacy"
        print(f"[JOB {job_id}] Step 1: Extracting CRM data ({mode_label})...")
        
        # Fetch tenant normalization config from Firestore (Hub data)
        db = get_firestore_client()
        tenant_doc = db.collection("tenants").document(tenant_id).get()
        stage_mapping = {}
        product_alias_map = {}
        if tenant_doc.exists:
            t_data = tenant_doc.to_dict()
            stage_mapping = t_data.get("crm", {}).get("stage_mapping", {})
            product_alias_map = t_data.get("product_alias_map", {})
            print(f"[JOB {job_id}] Applied {len(stage_mapping)} stage mappings, {len(product_alias_map)} product aliases")

        from core.normalization import generate_client_id
        client_id = generate_client_id(tenant_id, company_name)

        if use_structured:
            crm_entities = extract_entities_from_crm(
                payload, 
                stage_mapping=stage_mapping, 
                product_alias_map=product_alias_map
            )
            # Circular import risk again? select_subgraph is in main.py? 
            # No, it was in main.py. I should move it here or to a helper.
            from orchestrator_helpers import merge_tenant_knowledge_into_crm_entities
            crm_entities = merge_tenant_knowledge_into_crm_entities(crm_entities, tenant_id)
        else:
            crm_data = extract_from_crm_payload(payload, stage_mapping=stage_mapping)

        # Step 2: Parallel AI Extractions
        print(f"[JOB {job_id}] Step 2: Running parallel AI extractions...")
        _update_job(job_id, {"status": "analyzing_documents"})
        transcript = payload.get("sales_transcript")
        contract_pdf_url = payload.get("contract_pdf_url") or payload.get("contract_file_uri")

        async def safe_extract_transcript():
            if transcript and transcript.strip():
                async with EXTRACTION_SEMAPHORE:
                    return await extract_from_transcript(transcript)
            return None

        async def safe_extract_contract():
            if contract_pdf_url:
                try:
                    async with EXTRACTION_SEMAPHORE:
                        return await extract_from_contract(client_id, contract_pdf_url)
                except Exception as e:
                    _add_job_warning(job_id, f"contract_extraction_failed: {str(e)}")
                    return None
            return None

        transcript_data, contract_data = await asyncio.gather(
            safe_extract_transcript(), safe_extract_contract(),
        )

        # Step 3+: Branch by output format
        if use_structured:
            print(f"[JOB {job_id}] Step 3: Extracting structured entities...")
            _update_job(job_id, {"status": "extracting_entities"})
            async with EXTRACTION_SEMAPHORE:
                graph_data = await generate_structured_entities(
                    client_id=client_id, company_name=company_name, industry=industry,
                    crm_entities=crm_entities, transcript_data=transcript_data,
                    contract_data=contract_data, tenant_id=tenant_id,
                )
            e_count = len(graph_data.get("nodes", []))
            r_count = len(graph_data.get("edges", []))
            print(f"[JOB {job_id}] Extracted {e_count} entities, {r_count} edges")

            print(f"[JOB {job_id}] Step 4: Indexing structured graph...")
            _update_job(job_id, {"status": "indexing"})
            status = await index_structured_graph(client_id, graph_data, payload=payload)

            _update_job(job_id, {
                "status": "complete", "client_id": client_id,
                "graph_format": "structured", "entity_count": e_count,
                "edge_count": r_count, "entity_types": status.get("entity_types", []),
                "completed_at": datetime.utcnow().isoformat(),
            })
        else:
            print(f"[JOB {job_id}] Step 3: Generating markdown nodes...")
            _update_job(job_id, {"status": "generating_nodes"})
            async with EXTRACTION_SEMAPHORE:
                nodes = await generate_client_nodes(
                    client_id=client_id, company_name=company_name, industry=industry,
                    crm_data=crm_data, transcript_data=transcript_data,
                    contract_data=contract_data, tenant_id=tenant_id,
                )
            print(f"[JOB {job_id}] Generated {len(nodes)} nodes")

            _update_job(job_id, {"status": "writing_to_gcs"})
            uris = await write_all_nodes(client_id, nodes)
            _update_job(job_id, {"status": "indexing"})
            indexed = await index_all_nodes(client_id, nodes, payload=payload)

            _update_job(job_id, {
                "status": "complete", "client_id": client_id,
                "graph_format": "markdown", "node_count": len(nodes),
                "node_ids": [n.get("node_id") for n in nodes],
                "gcs_uris": uris, "completed_at": datetime.utcnow().isoformat(),
            })

        # Notify CSM
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
        _update_job(job_id, {
            "status": "failed", "error": str(e),
            "failed_at": datetime.utcnow().isoformat(),
        })
        print(f"[JOB {job_id}] Graph generation failed: {e}")
