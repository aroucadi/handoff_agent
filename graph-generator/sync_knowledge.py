from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, BackgroundTasks
from google.cloud import storage as gcs

from core.db import get_firestore_client
from extractors.knowledge_center_extractor import (
    crawl_knowledge_center,
    extract_entities_from_page,
)

router = APIRouter()

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Global semaphore to prevent run-away LLM usage across concurrent background tasks
EXTRACTION_SEMAPHORE = asyncio.Semaphore(3)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return slug or "unknown"


def _parse_gs_uri(uri: str) -> tuple[str, str]:
    raw = uri.replace("gs://", "", 1)
    parts = raw.split("/", 1)
    bucket = parts[0]
    prefix = parts[1].rstrip("/") + "/" if len(parts) > 1 and parts[1] else ""
    return bucket, prefix


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


def _fetch_http_website(start_uri: str, max_pages: int = 15) -> list[dict]:
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin, urlparse

    pages = []
    visited = set()
    queue = [start_uri]
    
    parsed_start = urlparse(start_uri)
    start_domain = parsed_start.netloc
    # Path boundary: restrict crawling to the starting directory or its subdirectories
    # This prevents wandering out of a specific bucket on shared hosts like storage.googleapis.com
    start_path_boundary = parsed_start.path.rsplit('/', 1)[0] + '/' if '/' in parsed_start.path else '/'

    while queue and len(pages) < max_pages:
        uri = queue.pop(0)
        if uri in visited:
            continue
        visited.add(uri)
        try:
            resp = requests.get(uri, timeout=15)
            resp.raise_for_status()

            if 'text/html' not in resp.headers.get('Content-Type', ''):
                continue

            soup = BeautifulSoup(resp.content, "html.parser")
            main = soup.find("main") or soup.find("body") or soup
            for tag in main.find_all(["header", "footer", "nav"]):
                tag.decompose()

            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else uri.split("/")[-1]
            text = main.get_text(separator="\n", strip=True)

            if text:
                pages.append({
                    "url": uri,
                    "title": title_text,
                    "category": "web",
                    "text_content": text
                })

            for a_tag in soup.find_all("a", href=True):
                next_uri = urljoin(uri, a_tag['href']).split('#')[0]
                parsed_next = urlparse(next_uri)
                if parsed_next.netloc == start_domain and parsed_next.path.startswith(start_path_boundary) and next_uri not in visited:
                    queue.append(next_uri)
        except Exception:
            continue

    return pages

def _fetch_pdf(uri: str) -> list[dict]:
    import requests
    import io
    import PyPDF2
    resp = requests.get(uri, timeout=15)
    resp.raise_for_status()
    reader = PyPDF2.PdfReader(io.BytesIO(resp.content))
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return [{
        "url": uri,
        "title": uri.split("/")[-1],
        "category": "document",
        "text_content": text
    }]

def _fetch_md(uri: str) -> list[dict]:
    import requests
    resp = requests.get(uri, timeout=15)
    resp.raise_for_status()
    return [{
        "url": uri,
        "title": uri.split("/")[-1],
        "category": "document",
        "text_content": resp.text
    }]

@router.post("/api/sync-knowledge/{tenant_id}")
async def sync_knowledge(tenant_id: str, background_tasks: BackgroundTasks):
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
async def get_sync_status(tenant_id: str):
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
            if stype == "website_crawl":
                if uri.startswith("http://") or uri.startswith("https://"):
                    p = _fetch_http_website(uri)
                    print(f"[SYNC] Crawled {len(p)} pages from {uri}")
                    pages.extend(p)
                elif uri.startswith("gs://"):
                    p = _crawl_knowledge_center_gcs(uri)
                    print(f"[SYNC] Scraped {len(p)} HTML files from GCS bucket {uri}")
                    pages.extend(p)
                else:
                    p = crawl_knowledge_center(uri)
                    print(f"[SYNC] Extracted {len(p)} local pages from {uri}")
                    pages.extend(p)
            elif stype == "document_upload":
                if uri.startswith("gs://"):
                    bucket_name, blob_name = _parse_gs_uri(uri)
                    client = gcs.Client()
                    blob = client.bucket(bucket_name).blob(blob_name)
                    pdf_bytes = blob.download_as_bytes()
                    import PyPDF2, io
                    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
                    pages.append({"url": uri, "title": uri.split("/")[-1], "category": "document", "text_content": text})
                else:
                    if uri.lower().endswith(".md"):
                        pages.extend(_fetch_md(uri))
                    else:
                        pages.extend(_fetch_pdf(uri))
            elif stype == "zendesk_api":
                print(f"⚠️ zendesk_api not fully implemented for {uri}")
                pass
            source_results.append({"source_id": source.get("source_id"), "status": "ok"})
        except Exception as e:
            print(f"[SYNC] Error extracting {uri}: {e}")
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
