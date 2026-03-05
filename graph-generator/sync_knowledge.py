from __future__ import annotations

import re
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from google.cloud import firestore
from google.cloud import storage as gcs

from extractors.knowledge_center_extractor import (
    crawl_knowledge_center,
    extract_entities_from_page,
)

router = APIRouter()
db = firestore.Client()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return slug or "unknown"


def _parse_gs_uri(uri: str) -> tuple[str, str]:
    raw = uri.replace("gs://", "", 1)
    parts = raw.split("/", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid GCS URI: {uri}")
    return parts[0], parts[1].rstrip("/") + "/"


def _crawl_knowledge_center_gcs(uri: str) -> list[dict]:
    from bs4 import BeautifulSoup

    bucket_name, prefix = _parse_gs_uri(uri)
    client = gcs.Client()
    bucket = client.bucket(bucket_name)
    pages: list[dict] = []

    for blob in bucket.list_blobs(prefix=prefix):
        if not blob.name.endswith(".html"):
            continue

        relative_path = blob.name[len(prefix):]
        if relative_path == "index.html":
            continue

        parts = relative_path.split("/")
        category = parts[0] if len(parts) > 1 else "general"

        html = blob.download_as_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")

        main = soup.find("main") or soup.find("body")
        if not main:
            continue

        for tag in main.find_all(["header", "footer", "nav"]):
            tag.decompose()

        title = soup.find("title")
        title_text = title.get_text(strip=True) if title else parts[-1].replace(".html", "")

        text = main.get_text(separator="\n", strip=True)
        pages.append({
            "url": relative_path,
            "title": title_text.split("—")[0].strip(),
            "category": category,
            "text_content": text,
        })

    return pages


def _normalize_product_ids(graph: dict) -> dict:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    id_map: dict[str, str] = {}
    for node in nodes:
        if node.get("type") != "Product":
            continue
        props = node.get("properties", {}) or {}
        name = props.get("name") or props.get("title") or ""
        new_id = f"product_{_slugify(name)}"
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


@router.post("/api/sync-knowledge/{tenant_id}")
async def sync_knowledge(tenant_id: str):
    tenant_doc = db.collection("tenants").document(tenant_id).get()
    if not tenant_doc.exists:
        raise HTTPException(404, f"Tenant {tenant_id} not found")

    tenant = tenant_doc.to_dict() or {}
    sources = tenant.get("knowledge_sources", [])
    if not sources:
        raise HTTPException(400, "Tenant has no knowledge_sources configured")

    pages: list[dict] = []
    source_results: list[dict] = []

    for source in sources:
        stype = (source.get("type") or "").strip()
        uri = (source.get("uri") or "").strip()
        if not stype or not uri:
            source_results.append({"source_id": source.get("source_id"), "status": "skipped", "reason": "missing type/uri"})
            continue

        if stype == "website_crawl":
            try:
                if uri.startswith("gs://"):
                    pages.extend(_crawl_knowledge_center_gcs(uri))
                else:
                    pages.extend(crawl_knowledge_center(uri))
                source_results.append({"source_id": source.get("source_id"), "type": stype, "uri": uri, "status": "ok"})
            except Exception as e:
                source_results.append({"source_id": source.get("source_id"), "type": stype, "uri": uri, "status": "error", "error": str(e)})
        else:
            source_results.append({"source_id": source.get("source_id"), "type": stype, "uri": uri, "status": "skipped", "reason": "not_implemented"})

    if not pages:
        raise HTTPException(400, "No knowledge pages discovered from configured sources")

    all_nodes: list[dict] = []
    all_edges: list[dict] = []
    seen_ids: set[str] = set()

    for page in pages:
        result = await extract_entities_from_page(page)
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
        "tenant_id": tenant_id,
        "status": "ready",
        "synced_at": _now_iso(),
        "entity_count": len(nodes),
        "edge_count": len(edges),
        "sources": source_results,
    })

    entities_ref = tenant_root.collection("entities")
    for node in nodes:
        entity_id = node.get("id", "")
        if not entity_id:
            continue
        entities_ref.document(entity_id).set({
            "entity_id": entity_id,
            "type": node.get("type", "Unknown"),
            "properties": node.get("properties", {}) or {},
            "tenant_id": tenant_id,
            "synced_at": _now_iso(),
        })

    edges_ref = tenant_root.collection("edges")
    for idx, edge in enumerate(edges):
        edges_ref.document(f"edge_{idx}").set({
            "type": edge.get("type", "RELATED_TO"),
            "from_id": edge.get("from_id", ""),
            "to_id": edge.get("to_id", ""),
            "properties": edge.get("properties", {}) or {},
            "tenant_id": tenant_id,
            "synced_at": _now_iso(),
        })

    db.collection("tenants").document(tenant_id).update({
        "knowledge_sources": sources,
        "updated_at": _now_iso(),
    })

    return {
        "tenant_id": tenant_id,
        "status": "ready",
        "sources": source_results,
        "pages_discovered": len(pages),
        "entity_count": len(nodes),
        "edge_count": len(edges),
        "product_id_map": graph.get("id_map", {}),
    }

