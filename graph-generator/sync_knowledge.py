from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, BackgroundTasks
from google.cloud import storage as gcs

from core.db import get_firestore_client
from google.cloud import firestore

from extractors.knowledge_center_extractor import (
    crawl_knowledge_center,
    extract_entities_from_page,
)

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Global semaphore to prevent run-away LLM usage across concurrent background tasks
EXTRACTION_SEMAPHORE = asyncio.Semaphore(3)

router = APIRouter()

from connectors import get_connector
from core.normalization import slugify


def _normalize_product_ids(graph: dict) -> dict:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    id_map: dict[str, str] = {}
    for node in nodes:
        if node.get("type") != "Product":
            continue
        props = node.get("properties", {}) or {}
        name = props.get("name") or props.get("title") or ""
        new_id = f"product_{slugify(name)}"
        old_id = node.get("id")
        if old_id and old_id != new_id:
            id_map[old_id] = new_id
            node["id"] = new_id

    if id_map:
        for edge in edges:
            if edge.get("from_id") in id_map:
                edge["from_id"] = id_map[edge["from_id"]]
            if edge.get("to_id") in id_map:
                edge["to_id"] = id_map[edge["to_id"]]

    seen = set()
    deduped_nodes = []
    for node in nodes:
        node_id = node.get("id")
        if not node_id or node_id in seen:
            continue
        seen.add(node_id)
        deduped_nodes.append(node)

    graph["nodes"] = deduped_nodes
    graph["edges"] = edges
    graph["id_map"] = id_map
    return graph

import os
from fastapi import Request

@router.post("/api/sync-knowledge/{tenant_id}")
async def sync_knowledge(tenant_id: str, request: Request, background_tasks: BackgroundTasks):
    # Enforce Admin Key
    admin_key = os.getenv("SYNAPSE_ADMIN_KEY")
    if not admin_key:
        # Prevent "effectively open" endpoint if env var is missing
        raise HTTPException(500, "Insecure Configuration: SYNAPSE_ADMIN_KEY is not set.")
        
    provided_key = request.headers.get("X-Synapse-Admin-Key")
    if provided_key != admin_key:
        raise HTTPException(403, "Invalid Admin Key")

    db = get_firestore_client()
    tenant_doc = db.collection("tenants").document(tenant_id).get()
    if not tenant_doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")

    tenant_root = db.collection("tenant_knowledge").document(tenant_id)
    tenant_root.set({
        "tenant_id": tenant_id, "status": "processing"
    }, merge=True)

    background_tasks.add_task(_run_sync_knowledge, tenant_id)
    return {"status": "started", "tenant_id": tenant_id}


@router.get("/api/sync-knowledge/{tenant_id}/status")
async def get_sync_status(tenant_id: str, request: Request):
    # Enforce Admin Key (Audit Alignment - Fail Closed)
    admin_key = os.getenv("SYNAPSE_ADMIN_KEY")
    if not admin_key:
        raise HTTPException(500, "Insecure Configuration: SYNAPSE_ADMIN_KEY is not set.")
        
    provided_key = request.headers.get("X-Synapse-Admin-Key")
    if provided_key != admin_key:
        raise HTTPException(403, "Invalid Admin Key")

    db = get_firestore_client()
    doc = db.collection("tenant_knowledge").document(tenant_id).get()
    if not doc.exists:
        return {"status": "not_found"}
    return doc.to_dict()


async def _run_sync_knowledge(tenant_id: str):
    db = get_firestore_client()
    tenant_doc = db.collection("tenants").document(tenant_id).get()
    if not tenant_doc.exists:
        print(f"[SYNC] Tenant {tenant_id} not found")
        return

    tenant = tenant_doc.to_dict() or {}
    sources = tenant.get("knowledge_sources", [])
    if not sources:
        print(f"[SYNC] Tenant {tenant_id} has no knowledge_sources configured")
        return

    # Create the document with 'processing' status
    tenant_root = db.collection("tenant_knowledge").document(tenant_id)
    tenant_root.set({
        "tenant_id": tenant_id, "status": "processing", "synced_at": _now_iso()
    })

    pages: list[dict] = []
    source_results: list[dict] = []
    print(f"[SYNC] Starting knowledge sync for tenant: {tenant_id}")
    print(f"[SYNC] Found {len(sources)} knowledge sources")

    for source in sources:
        stype = (source.get("type") or "").strip()
        uri = (source.get("uri") or "").strip()
        print(f"[SYNC] Processing source: type={stype}, uri={uri}")
        if not stype or not uri:
            continue

        try:
            connector = get_connector(stype, uri)
            p = await connector.fetch_pages(uri, config=source.get("config", {}))
            print(f"[SYNC] Connector {stype} fetched {len(p)} pages from {uri}")
            pages.extend(p)
            source_results.append({"source_id": source.get("source_id"), "status": "ok"})
        except Exception as e:
            print(f"[SYNC] Error extracting {uri} via {stype}: {e}")
            source_results.append({"source_id": source.get("source_id"), "status": "error", "error": str(e)})

    print(f"[SYNC] Total pages discovered: {len(pages)}")
    if not pages:
        print("[SYNC] Error: No pages discovered. Returning 400.")
        raise HTTPException(400, "No knowledge pages discovered")

    all_nodes: list[dict] = []
    all_edges: list[dict] = []
    seen_ids: set[str] = set()

    # Wrap the LLM call to respect the global concurrency limit
    async def _safe_extract(p: dict) -> dict:
        async with EXTRACTION_SEMAPHORE:
            return await extract_entities_from_page(p)

    for page in pages:
        result = await _safe_extract(page)
        if not result:
            continue
        for node in result.get("nodes", []):
            node_id = node.get("id")
            if not node_id or node_id in seen_ids:
                continue
            seen_ids.add(node_id)
            all_nodes.append(node)
        all_edges.extend(result.get("edges", []))

    graph = _normalize_product_ids({"nodes": all_nodes, "edges": all_edges})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    tenant_root = db.collection("tenant_knowledge").document(tenant_id)
    tenant_root.set({
        "tenant_id": tenant_id, "status": "ready", "synced_at": _now_iso(),
        "entity_count": len(nodes), "edge_count": len(edges),
    })

    entities_ref = tenant_root.collection("entities")
    for node in nodes:
        entity_id = node.get("id", "")
        entities_ref.document(entity_id).set({
            "entity_id": entity_id, "type": node.get("type"),
            "properties": node.get("properties"), "tenant_id": tenant_id,
        })

    edges_ref = tenant_root.collection("edges")
    for idx, edge in enumerate(edges):
        edges_ref.document(f"edge_{idx}").set({
            "type": edge.get("type"), "from_id": edge.get("from_id"),
            "to_id": edge.get("to_id"), "properties": edge.get("properties"),
            "tenant_id": tenant_id,
        })

    return {"status": "ready", "entity_count": len(nodes)}
