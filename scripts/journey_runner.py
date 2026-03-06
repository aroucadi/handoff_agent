from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import httpx
from google.cloud import firestore, storage

sys.path.append(str(Path(__file__).parent.parent))
from core.config import config

crm_sim_path = Path(__file__).parent.parent / "crm-simulator"
sys.path.append(str(crm_sim_path))
from seed_data import DEMO_DEALS

scripts_path = Path(__file__).parent
sys.path.append(str(scripts_path))
from generate_contracts import generate_pdf_contract


@dataclass
class ServiceUrls:
    hub: str
    crm: str
    graph: str
    backend: str


def _now() -> str:
    return datetime.utcnow().isoformat()


def _slug_company(name: str) -> str:
    return name.lower().replace(" ", "-").replace(",", "").replace(".", "")


async def _get_json(url: str, timeout: float = 60.0) -> dict:
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def _post_json(url: str, payload: dict | None = None, timeout: float = 120.0) -> dict:
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload or {})
        resp.raise_for_status()
        return resp.json()


async def _patch_json(url: str, payload: dict, timeout: float = 120.0) -> dict:
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.patch(url, json=payload)
        resp.raise_for_status()
        return resp.json()


def _delete_collection(db: firestore.Client, coll_ref: firestore.CollectionReference, batch_size: int = 200):
    docs = list(coll_ref.limit(batch_size).stream())
    for doc in docs:
        for sub in doc.reference.collections():
            _delete_collection(db, sub, batch_size=batch_size)
        doc.reference.delete()
    if len(docs) >= batch_size:
        _delete_collection(db, coll_ref, batch_size=batch_size)


def clean_state(preserve_industries: bool = True):
    db = firestore.Client(project=config.project_id)
    collections = [
        "notifications",
        "skill_graphs",
        "knowledge_graphs",
        "agent_traces",
        "sessions",
        "client_insights",
        "deals",
        "tenant_knowledge",
        "skill_graph_nodes",
        "tenants",
    ]
    for c in collections:
        _delete_collection(db, db.collection(c), batch_size=200)

    gcs = storage.Client(project=config.project_id)
    sg_bucket = gcs.bucket(config.skill_graphs_bucket)
    up_bucket = gcs.bucket(config.uploads_bucket)

    prefixes = ["clients/", "product/"]
    if not preserve_industries:
        prefixes.append("industries/")
    for prefix in prefixes:
        blobs = list(sg_bucket.list_blobs(prefix=prefix))
        for b in blobs:
            b.delete()

    contract_blobs = list(up_bucket.list_blobs(prefix="contracts/"))
    for b in contract_blobs:
        b.delete()


async def healthcheck(urls: ServiceUrls):
    await _get_json(f"{urls.hub.rstrip('/')}/health")
    await _get_json(f"{urls.crm.rstrip('/')}/health")
    await _get_json(f"{urls.graph.rstrip('/')}/health")
    await _get_json(f"{urls.backend.rstrip('/')}/health")


async def tenant_onboard(urls: ServiceUrls, tenant_name: str, kc_uri: str) -> str:
    tenant = await _post_json(
        f"{urls.hub.rstrip('/')}/api/tenants",
        {"name": tenant_name, "brand_name": "ClawdView", "crm_type": "custom"},
        timeout=30.0,
    )
    tenant_id = tenant["tenant_id"]

    await _patch_json(
        f"{urls.hub.rstrip('/')}/api/tenants/{tenant_id}",
        {
            "crm": {
                "crm_type": "custom",
                "crm_url": urls.crm.rstrip("/"),
                "connected": True,
                "auth_method": "api_key",
            },
            "knowledge_sources": [
                {"type": "website_crawl", "uri": kc_uri, "name": "ClawdView Knowledge Center"}
            ],
            "status": "active",
        },
        timeout=30.0,
    )

    products = [
        {"name": "ClawdView AgilePlace", "description": "Enterprise agile delivery and Kanban"},
        {"name": "ClawdView Portfolios", "description": "Strategic portfolio planning and alignment"},
        {"name": "ClawdView Hub", "description": "Integrations, mappings, and bidirectional sync"},
        {"name": "ClawdView PPM Pro", "description": "Project portfolio management for enterprises"},
    ]
    for p in products:
        await _post_json(f"{urls.hub.rstrip('/')}/api/tenants/{tenant_id}/products", p, timeout=30.0)

    print("\n[RUNNER] Triggering knowledge generation (background)...")
    await _post_json(f"{urls.hub.rstrip('/')}/api/tenants/{tenant_id}/generate-knowledge", timeout=120.0)

    print("[RUNNER] Waiting for knowledge generation to complete...")
    for _ in range(30):
        await asyncio.sleep(10)
        tenant_status = await _get_json(f"{urls.hub.rstrip('/')}/api/tenants/{tenant_id}", timeout=10.0)
        products_list = tenant_status.get("products", [])
        if all(p.get("knowledge_generated") for p in products_list):
            print(f"[RUNNER] Knowledge generation complete for all {len(products_list)} products!")
            break
        generated_count = len([p for p in products_list if p.get("knowledge_generated")])
        print(f"[RUNNER] Progress: {generated_count}/{len(products_list)} products generated...")
    else:
        print("[RUNNER] WARNING: Knowledge generation timed out (polling stopped).")
    print("\n[RUNNER] Triggering knowledge center sync (background)...")
    await _post_json(f"{urls.hub.rstrip('/')}/api/tenants/{tenant_id}/sync-knowledge", timeout=120.0)

    print("[RUNNER] Waiting for knowledge sync to complete (may take up to 5 minutes due to AI quotas)...")
    for _ in range(60):
        await asyncio.sleep(10)
        try:
            status_resp = await _get_json(f"{urls.graph.rstrip('/')}/api/sync-knowledge/{tenant_id}/status", timeout=15.0)
            status = status_resp.get("status")
            if status == "ready":
                print(f"[RUNNER] Knowledge sync complete! Found {status_resp.get('entity_count')} entities.")
                break
            elif status == "error":
                print(f"[RUNNER] WARNING: Knowledge sync failed: {status_resp}")
                break
            print(f"[RUNNER] Still syncing... ({status})")
        except (httpx.NetworkError, httpx.TimeoutException) as e:
            print(f"[RUNNER] Transient connection error polling status: {e}. Retrying in 10s...")
    else:
        print("[RUNNER] WARNING: Knowledge sync timed out after 10 minutes.")

    return tenant_id


async def tenant_onboard_negative(urls: ServiceUrls, tenant_name: str, kc_uri: str) -> str:
    tenant = await _post_json(
        f"{urls.hub.rstrip('/')}/api/tenants",
        {"name": tenant_name, "brand_name": "ClawdView", "crm_type": "custom"},
        timeout=30.0,
    )
    tenant_id = tenant["tenant_id"]

    bad_mapping = {
        "deal_idx": "deal_id",
        "company_name": "company_name",
        "deal_value": "deal_value",
        "close_date": "close_date",
        "industry": "industry",
        "employee_count": "employee_count",
        "products": "products",
        "contacts": "contacts",
        "risks": "risks",
        "success_metrics": "success_metrics",
        "sales_transcript": "sales_transcript",
        "contract_pdf_url": "contract_pdf_url",
        "contract_file_uri": "contract_file_uri",
        "csm_id": "csm_id",
    }

    await _patch_json(
        f"{urls.hub.rstrip('/')}/api/tenants/{tenant_id}",
        {
            "crm": {
                "crm_type": "custom",
                "crm_url": urls.crm.rstrip("/"),
                "connected": True,
                "auth_method": "api_key",
                "field_mapping": bad_mapping,
            },
            "knowledge_sources": [
                {"type": "website_crawl", "uri": kc_uri, "name": "ClawdView Knowledge Center"}
            ],
            "status": "active",
        },
        timeout=30.0,
    )

    return tenant_id


async def _crm_patch(urls: ServiceUrls, deal_id: str, payload: dict):
    await _patch_json(f"{urls.crm.rstrip('/')}/api/deals/{deal_id}", payload, timeout=20.0)


async def _crm_stage(urls: ServiceUrls, deal_id: str, stage: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{urls.crm.rstrip('/')}/api/deals/{deal_id}/stage", params={"stage": stage})
        resp.raise_for_status()
        return resp.json()


async def _crm_update_transcript(urls: ServiceUrls, deal_id: str, transcript: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{urls.crm.rstrip('/')}/api/deals/{deal_id}/update-transcript",
            data={"transcript": transcript},
        )
        resp.raise_for_status()


async def _crm_upload_contract(urls: ServiceUrls, deal_id: str, pdf_path: Path):
    async with httpx.AsyncClient(timeout=60.0) as client:
        with open(pdf_path, "rb") as f:
            resp = await client.post(
                f"{urls.crm.rstrip('/')}/api/deals/{deal_id}/upload-contract",
                files={"file": (pdf_path.name, f, "application/pdf")},
            )
        resp.raise_for_status()
        return resp.json()


async def seed_deals_via_crm(urls: ServiceUrls, tenant_id: str, out_dir: Path, lite: bool = False):
    deals_to_process = DEMO_DEALS[:3] if lite else DEMO_DEALS
    for deal in deals_to_process:
        # 1. Try to associate existing deal with tenant (Upsert Pattern)
        try:
            print(f"[SEED] Patching deal {deal.deal_id} for tenant {tenant_id}...")
            await _crm_patch(urls, deal.deal_id, {"tenant_id": tenant_id, "crm_platform": deal.crm_platform})
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"[SEED] Deal {deal.deal_id} missing. Creating fresh...")
                # Use POST to create from scratch using the full seed data
                payload = deal.model_dump(mode="json")
                payload["tenant_id"] = tenant_id # Ensure it belongs to our new tenant
                await _post_json(f"{urls.crm.rstrip('/')}/api/deals", payload)
            else:
                raise

        transcript = deal.sales_transcript or ""
        if transcript.strip():
            await _crm_update_transcript(urls, deal.deal_id, transcript)

        pdf_path = out_dir / f"{deal.deal_id}_contract.pdf"
        generate_pdf_contract(deal, pdf_path)
        await _crm_upload_contract(urls, deal.deal_id, pdf_path)

        await _crm_stage(urls, deal.deal_id, deal.stage.value)
        
        if lite:
            print("    ⏳ [LITE MODE] Pausing 5s before NEXT deal to throttle CRM Webhook -> Graph Gen pipeline...")
            await asyncio.sleep(5)


async def seed_negative_deal(urls: ServiceUrls, tenant_id: str, out_dir: Path):
    new_deal = await _post_json(
        f"{urls.crm.rstrip('/')}/api/deals",
        {
            "deal_id": "COMP-REJECT-001",
            "company_name": "PharmaLink Compliance-Heavy Int.",
            "deal_value": 123000,
            "stage": "closed_won",
            "industry": "tech",
            "employee_count": 1200,
            "crm_platform": "custom",
            "tenant_id": tenant_id,
            "products": [{"name": "ClawdView Hub", "annual_value": 250000}],
            "contacts": [{"name": "Ava Test", "title": "VP Ops", "role": "champion"}],
            "success_metrics": [{"metric": "Time-to-Value", "current_value": "unknown", "target_value": "30 days", "timeframe": "Q2"}],
            "risks": [{"description": "Mapping intentionally broken", "severity": "high", "source": "demo"}],
        },
        timeout=30.0,
    )
    deal_id = new_deal["deal_id"]

    class _TmpDeal:
        def __init__(self):
            self.deal_id = deal_id
            self.company_name = "PharmaLink Compliance-Heavy Int."
            self.industry = "tech"
            self.employee_count = 1200
            self.products = [type("P", (), {"name": "ClawdView Hub", "annual_value": 250000})()]
            self.deal_value = 123000
            self.close_date = None
            self.sla_days = 60

    pdf_path = out_dir / f"{deal_id}_contract.pdf"
    generate_pdf_contract(_TmpDeal(), pdf_path)
    await _crm_upload_contract(urls, deal_id, pdf_path)

    await _crm_stage(urls, deal_id, "closed_won")


async def wait_for_graph_ready(tenant_id: str, deal_id: str, company_name: str, timeout_s: int = 900) -> dict:
    db = firestore.Client(project=config.project_id)
    doc_ref = db.collection("deals").document(tenant_id).collection("items").document(deal_id)
    start = time.time()
    backoff = 1.0
    while time.time() - start < timeout_s:
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict() or {}
            if data.get("graph_ready") is True:
                return data
        await asyncio.sleep(backoff)
        backoff = min(backoff * 1.4, 15.0)
    raise TimeoutError(f"Timed out waiting for graph_ready: {tenant_id} {deal_id} {company_name}")


async def verify_outputs(urls: ServiceUrls, client_id: str):
    await _post_json(f"{urls.backend.rstrip('/')}/api/clients/{client_id}/outputs/briefing", {"user_role": "csm"}, timeout=300.0)
    await _post_json(f"{urls.backend.rstrip('/')}/api/clients/{client_id}/outputs/action-plan", {"user_role": "csm"}, timeout=300.0)


async def main():
    parser = argparse.ArgumentParser(description="Synapse end-to-end journey runner (UI-equivalent seeding)")
    parser.add_argument("--hub_url", default="http://localhost:8003")
    parser.add_argument("--crm_url", default="http://localhost:8001")
    parser.add_argument("--graph_url", default="http://localhost:8002")
    parser.add_argument("--backend_url", default="http://localhost:8000")
    parser.add_argument("--kc_uri", default=str(Path(__file__).parent.parent / "knowledge-center"))
    parser.add_argument("--skip_clean", action="store_true")
    parser.add_argument("--lite", action="store_true", help="Limit to 3 deals and stagger delays to prevent API abuse")
    args = parser.parse_args()

    urls = ServiceUrls(hub=args.hub_url, crm=args.crm_url, graph=args.graph_url, backend=args.backend_url)

    # Auto-resolve kc_uri to HTTPS if hitting production
    kc_uri = args.kc_uri
    is_local = kc_uri.lower().startswith("d:\\") or kc_uri.startswith("/")
    if "localhost" not in args.hub_url and is_local:
        # If we are hitting a remote hub but using a local path, switch to the public static site URL
        project_id = config.project_id
        kc_uri = f"https://storage.googleapis.com/{project_id}-knowledge-center/index.html"
        print(f"[INFO] Remote Hub detected. Switching kc_uri to: {kc_uri}")

    if not args.skip_clean:
        clean_state()

    await healthcheck(urls)

    tenant_id = await tenant_onboard(urls, "ClawdView Global Enterprise", kc_uri)
    neg_tenant_id = await tenant_onboard_negative(urls, "ClawdView Regulatory High-Security", kc_uri)

    out_dir = Path(__file__).parent.parent / "crm-simulator" / "uploads" / "contracts"
    out_dir.mkdir(parents=True, exist_ok=True)

    await seed_negative_deal(urls, neg_tenant_id, out_dir)

    db = firestore.Client(project=config.project_id)
    neg_doc = db.collection("tenants").document(neg_tenant_id).get()
    neg_status = (neg_doc.to_dict() or {}).get("integration_status")
    if neg_status != "error":
        raise RuntimeError(f"Expected integration_status=error for negative tenant, got {neg_status}")

    await seed_deals_via_crm(urls, tenant_id, out_dir, lite=args.lite)

    deals_to_process = DEMO_DEALS[:3] if args.lite else DEMO_DEALS
    for deal in deals_to_process:
        summary = await wait_for_graph_ready(tenant_id, deal.deal_id, deal.company_name, timeout_s=900)
        client_id = summary.get("client_id") or f"{tenant_id}_{_slug_company(deal.company_name)}"
        await verify_outputs(urls, client_id)

    report = {
        "project_id": config.project_id,
        "tenant_id": tenant_id,
        "negative_tenant_id": neg_tenant_id,
        "hub": urls.hub,
        "crm": urls.crm,
        "graph": urls.graph,
        "backend": urls.backend,
        "timestamp": _now(),
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
