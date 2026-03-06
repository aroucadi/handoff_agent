"""Synapse — Full End-to-End Seeding Orchestrator.

Simulates the REAL user journey through the deployed Synapse ecosystem:

  1. CLEAN   — Purge all Firestore collections + GCS buckets
  2. CONTRACTS — Generate realistic PDF contracts and upload to GCS
  3. HUB     — Create tenant via Hub API (as if user filled the wizard)
  4. CRM     — Reset CRM deals (simulates CRM restart with seed data)
  5. WEBHOOK — Trigger stage transitions to "closed_won" via CRM API
                → This fires the webhook to Graph Generator (realistic flow)
  6. RAG     — Seed remaining deals (non-won) via direct webhook
  7. VERIFY  — Check Firestore for generated graphs

Usage:
    py scripts/seed_all.py --api_url <API> --crm_url <CRM> --hub_url <HUB> --graph_url <GRAPH>

    Or with defaults from Terraform outputs:
    py scripts/seed_all.py
"""

import asyncio
import argparse
import sys
import os
import time
from pathlib import Path

# Add root to sys path
sys.path.append(str(Path(__file__).parent.parent))
crm_sim_path = Path(__file__).parent.parent / "crm-simulator"
sys.path.append(str(crm_sim_path))

import httpx
from google.cloud import firestore, storage
from core.config import config

# Default deployed URLs (from Terraform outputs)
DEFAULT_API_URL = "https://synapse-api-uicugotuta-uc.a.run.app"
DEFAULT_CRM_URL = "https://synapse-crm-simulator-uicugotuta-uc.a.run.app"
DEFAULT_HUB_URL = "https://synapse-hub-uicugotuta-uc.a.run.app"
DEFAULT_GRAPH_URL = "https://synapse-graph-generator-uicugotuta-uc.a.run.app"


def banner(step: int, total: int, title: str):
    print(f"\n{'='*60}")
    print(f"  [{step}/{total}] {title}")
    print(f"{'='*60}")


# ── Step 1: CLEAN ──────────────────────────────────────────────
def step_clean():
    """Purge all Firestore collections and GCS buckets."""
    banner(1, 7, "CLEANING — Purging Firestore + GCS")

    db = firestore.Client(project=config.project_id)

    collections = [
        "notifications",
        "skill_graphs",
        "agent_traces",
        "sessions",
        "client_insights",
        "tenants",  # Hub tenant configs too
    ]

    for coll_name in collections:
        print(f"  Purging: {coll_name}")
        coll_ref = db.collection(coll_name)
        docs = coll_ref.limit(500).stream()
        count = 0
        for doc in docs:
            # Delete subcollections recursively
            for sub_coll in doc.reference.collections():
                for sub_doc in sub_coll.stream():
                    sub_doc.reference.delete()
            doc.reference.delete()
            count += 1
        print(f"    Deleted {count} documents")

    # GCS cleanup
    gcs = storage.Client(project=config.project_id)
    for bucket_name, prefix in [
        (config.skill_graphs_bucket, "clients/"),
        (config.uploads_bucket, "contracts/"),
    ]:
        print(f"  Purging GCS: gs://{bucket_name}/{prefix}")
        try:
            bucket = gcs.bucket(bucket_name)
            blobs = list(bucket.list_blobs(prefix=prefix))
            if blobs:
                for blob in blobs:
                    blob.delete()
                print(f"    Deleted {len(blobs)} objects")
            else:
                print(f"    (empty)")
        except Exception as e:
            print(f"    ⚠️ {e}")

    print("  ✅ Cleanup complete")


# ── Step 2: GENERATE & UPLOAD CONTRACTS ────────────────────────
def step_contracts():
    """Generate realistic PDF contracts and upload to GCS."""
    banner(2, 7, "CONTRACTS — Generating & Uploading PDFs")

    try:
        from fpdf import FPDF
    except ImportError:
        print("  ⚠️ fpdf2 not installed, installing...")
        os.system(f"{sys.executable} -m pip install fpdf2 -q")
        from fpdf import FPDF

    from seed_data import DEMO_DEALS
    from generate_contracts import generate_pdf_contract

    out_dir = Path(__file__).parent.parent / "crm-simulator" / "uploads" / "contracts"
    out_dir.mkdir(parents=True, exist_ok=True)

    client = storage.Client(project=config.project_id)
    bucket = client.bucket(config.uploads_bucket)

    for deal in DEMO_DEALS:
        file_name = f"{deal.deal_id}_contract.pdf"
        file_path = out_dir / file_name
        generate_pdf_contract(deal, file_path)
        blob = bucket.blob(f"contracts/{file_name}")
        blob.upload_from_filename(str(file_path))
        print(f"  📄 {file_name} → gs://{config.uploads_bucket}/contracts/{file_name}")

    print(f"  ✅ Generated & uploaded {len(DEMO_DEALS)} PDF contracts")


# ── Step 3: CONFIGURE HUB TENANT (via API) ─────────────────────
async def step_hub(hub_url: str, crm_url: str, graph_url: str):
    """Create/configure the tenant via Hub API — simulates wizard UI."""
    banner(3, 7, "HUB — Configuring Tenant via API")

    graph_webhook = f"{graph_url.rstrip('/')}/generate"

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 3a: Create tenant (as if user clicked "Create Tenant" in wizard)
        print("  Creating tenant via POST /api/tenants ...")
        resp = await client.post(f"{hub_url}/api/tenants", json={
            "name": "ClawdView Global Enterprise",
            "brand_name": "ClawdView",
            "crm_type": "custom",
        })
        if resp.status_code == 201:
            tenant = resp.json()
            tenant_id = tenant["tenant_id"]
            print(f"  ✅ Tenant created: {tenant_id}")
        else:
            print(f"  ⚠️ Tenant creation returned {resp.status_code}: {resp.text[:200]}")
            # Use fallback tenant_id
            tenant_id = "default-tenant"
            # Try creating with explicit ID directly in Firestore
            db = firestore.Client(project=config.project_id)
            db.collection("tenants").document(tenant_id).set({
                "tenant_id": tenant_id,
                "name": "ClawdView Global Enterprise",
                "brand_name": "ClawdView",
                "status": "configuring",
                "crm": {"crm_type": "custom", "connected": False},
                "products": [],
                "agent": {"roles": ["csm", "sales", "support", "win-back"]},
            })
            print(f"  ✅ Fallback tenant '{tenant_id}' created in Firestore")

        # Step 3b: Configure CRM connection (as if user filled CRM wizard step)
        print(f"  Configuring CRM connection via PATCH /api/tenants/{tenant_id} ...")
        resp = await client.patch(f"{hub_url}/api/tenants/{tenant_id}", json={
            "crm": {
                "crm_type": "custom",
                "crm_url": crm_url,
                "connected": True,
                "auth_method": "api_key",
                "field_mapping": {
                    "deal_id": "deal_id",
                    "company_name": "company_name",
                    "deal_value": "deal_value",
                    "close_date": "close_date",
                    "industry": "industry",
                    "products": "products",
                    "contacts": "contacts",
                    "risks": "risks",
                    "success_metrics": "success_metrics",
                    "sales_transcript": "sales_transcript",
                    "contract_pdf_url": "contract_pdf_url",
                },
            },
            "webhook_url": graph_webhook,
        })
        if resp.status_code == 200:
            print(f"  ✅ CRM connected → {crm_url}")
            print(f"  ✅ Webhook URL → {graph_webhook}")
        else:
            print(f"  ⚠️ CRM config returned {resp.status_code}: {resp.text[:200]}")

        # Step 3c: Add products (as if user clicked "Add Product" for each)
        products = [
            {"name": "ClawdView AgilePlace", "description": "Enterprise Agile project management and Kanban boards"},
            {"name": "ClawdView Portfolios", "description": "Strategic portfolio management and resource planning"},
            {"name": "ClawdView Hub", "description": "Integration and ETL hub for bidirectional data flow"},
            {"name": "ClawdView PPM Pro", "description": "Project and Portfolio management for enterprises"},
        ]
        for product in products:
            resp = await client.post(
                f"{hub_url}/api/tenants/{tenant_id}/products",
                json=product,
            )
            if resp.status_code == 201:
                p = resp.json()
                print(f"  📦 Added product: {p['name']} (node_id: {p['node_id']})")
            else:
                print(f"  ⚠️ Product '{product['name']}' → {resp.status_code}")

        # Step 3d: Activate tenant (as if user clicked "Go Live")
        resp = await client.patch(f"{hub_url}/api/tenants/{tenant_id}", json={
            "status": "active",
            "agent": {
                "roles": ["csm", "sales", "support", "win-back"],
                "persona": "Professional, data-driven, and proactive enterprise assistant for ClawdView customers.",
                "brand_name": "ClawdView",
            },
        })
        if resp.status_code == 200:
            print(f"  ✅ Tenant activated")
        else:
            print(f"  ⚠️ Activation returned {resp.status_code}")

    return tenant_id


# ── Step 4: RESET CRM DEALS ───────────────────────────────────
async def step_crm_reset(crm_url: str):
    """Reset CRM data — simulates fresh deal pipeline."""
    banner(4, 7, "CRM — Resetting Deal Pipeline")

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(f"{crm_url}/api/reset")
        if resp.status_code == 200:
            body = resp.json()
            print(f"  ✅ CRM reset: {body.get('count', '?')} deals loaded")
        else:
            print(f"  ⚠️ CRM reset returned {resp.status_code}: {resp.text[:200]}")


# ── Step 5: TRIGGER STAGE TRANSITIONS (CLOSED WON) ────────────
async def step_trigger_won(crm_url: str):
    """Transition 'closed_won' deals via CRM API — triggers webhook pipeline."""
    banner(5, 7, "WEBHOOKS — Triggering Stage Transitions to Closed Won")

    from seed_data import DEMO_DEALS

    won_deals = [d for d in DEMO_DEALS if d.stage.value == "closed_won"]
    print(f"  Found {len(won_deals)} deals marked as closed_won in seed data")
    print(f"  Transitioning them through the CRM Kanban → fires webhook → Graph Generator")

    async with httpx.AsyncClient(timeout=30.0) as client:
        for deal in won_deals:
            print(f"\n  🔄 {deal.deal_id} ({deal.company_name}) — ${deal.deal_value:,.0f}")
            # First set to negotiation, then to closed_won (realistic flow)
            resp = await client.post(
                f"{crm_url}/api/deals/{deal.deal_id}/stage",
                params={"stage": "negotiation"},
            )
            if resp.status_code != 200:
                print(f"    ⚠️ Stage→negotiation failed: {resp.status_code} {resp.text[:100]}")
                continue

            await asyncio.sleep(2)  # Brief pause like a real user

            resp = await client.post(
                f"{crm_url}/api/deals/{deal.deal_id}/stage",
                params={"stage": "closed_won"},
            )
            if resp.status_code == 200:
                body = resp.json()
                webhook_status = body.get("webhook_fired", "unknown")
                print(f"    ✅ Closed Won! Webhook fired: {webhook_status}")
            else:
                print(f"    ⚠️ Stage→closed_won failed: {resp.status_code}")

            # Rate limit: wait for Gemini to process graph generation
            print(f"    ⏳ Waiting 10s for Gemini quota...")
            await asyncio.sleep(10)


# ── Step 6: SEED REMAINING DEALS (via webhook) ────────────────
async def step_seed_remaining(api_url: str):
    """Seed non-won deals via the Synapse API webhook endpoint."""
    banner(6, 7, "RAG — Seeding Remaining Deals via Webhook")

    from seed_data import DEMO_DEALS

    non_won_deals = [d for d in DEMO_DEALS if d.stage.value != "closed_won"]
    print(f"  Seeding {len(non_won_deals)} non-won deals via API webhook")

    webhook_url = f"{api_url}/api/webhooks/crm/deal-closed"

    # Group by company for historical context
    companies: dict[str, list] = {}
    for deal in DEMO_DEALS:
        companies.setdefault(deal.company_name, []).append(deal)

    async with httpx.AsyncClient(timeout=30.0) as client:
        for idx, deal in enumerate(non_won_deals, 1):
            historical = [
                {
                    "deal_id": d.deal_id,
                    "stage": d.stage.value,
                    "deal_value": d.deal_value,
                    "close_date": str(d.close_date) if d.close_date else None,
                }
                for d in companies[deal.company_name]
                if d.deal_id != deal.deal_id
            ]

            payload = {
                "deal_id": deal.deal_id,
                "company_name": deal.company_name,
                "deal_value": deal.deal_value,
                "industry": deal.industry,
                "employee_count": deal.employee_count,
                "close_date": deal.close_date.isoformat() if deal.close_date else None,
                "products": [{"name": p.name, "annual_value": p.annual_value} for p in deal.products],
                "contacts": [
                    {"name": c.name, "title": c.title, "role": c.role, "pain_point": c.pain_point}
                    for c in deal.contacts
                ],
                "risks": [{"description": r.description, "severity": r.severity, "source": r.source} for r in deal.risks],
                "success_metrics": [
                    {"metric": m.metric, "current_value": m.current_value, "target_value": m.target_value}
                    for m in deal.success_metrics
                ],
                "sales_transcript": deal.sales_transcript or "",
                "contract_pdf_url": f"gs://{config.uploads_bucket}/contracts/{deal.deal_id}_contract.pdf",
                "historical_deals": historical,
            }

            try:
                resp = await client.post(webhook_url, json=payload, timeout=60.0)
                status = "✅" if resp.status_code in [200, 202] else "⚠️"
                msg = resp.json().get("message", resp.text[:80]) if resp.status_code in [200, 202] else resp.text[:80]
                print(f"  [{idx}/{len(non_won_deals)}] {status} {deal.deal_id} ({deal.company_name}) — {msg}")
            except Exception as e:
                print(f"  [{idx}/{len(non_won_deals)}] ❌ {deal.deal_id} — {e}")

            # Rate limit: wait for Gemini API quota to reset
            print(f"    ⏳ Waiting 10s for Gemini quota...")
            await asyncio.sleep(10)


# ── Step 7: VERIFY ─────────────────────────────────────────────
def step_verify():
    """Check Firestore for generated graphs and tenant configuration."""
    banner(7, 7, "VERIFY — Checking Firestore State")

    db = firestore.Client(project=config.project_id)

    # Check tenants
    tenants = list(db.collection("tenants").stream())
    print(f"  Tenants: {len(tenants)}")
    for t in tenants:
        data = t.to_dict()
        print(f"    • {data.get('name', '?')} [{data.get('status', '?')}] — CRM: {data.get('crm', {}).get('crm_url', 'N/A')}")
        products = data.get("products", [])
        print(f"      Products: {len(products)} — {', '.join(p.get('name', '?') for p in products)}")

    # Check skill_graphs
    graphs = list(db.collection("skill_graphs").stream())
    print(f"\n  Skill Graphs: {len(graphs)}")
    for g in graphs:
        data = g.to_dict()
        status = data.get("status", "unknown")
        nodes = len(list(g.reference.collection("nodes").stream()))
        print(f"    • {g.id}: status={status}, nodes={nodes}")

    # Check notifications
    notifications = list(db.collection("notifications").stream())
    print(f"\n  Notifications: {len(notifications)}")

    print(f"\n  ✅ Verification complete")


# ── Main Orchestrator ──────────────────────────────────────────
async def main(api_url: str, crm_url: str, hub_url: str, graph_url: str):
    print("╔══════════════════════════════════════════════════════╗")
    print("║    SYNAPSE — Full End-to-End Seeding Orchestrator    ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"  API:   {api_url}")
    print(f"  CRM:   {crm_url}")
    print(f"  Hub:   {hub_url}")
    print(f"  Graph: {graph_url}")
    print(f"  Project: {config.project_id}")

    # 1. Clean
    step_clean()

    # 2. Generate & upload contracts
    step_contracts()

    # 3. Configure Hub tenant via API
    tenant_id = await step_hub(hub_url, crm_url, graph_url)

    # 4. Reset CRM deals
    await step_crm_reset(crm_url)

    # 5. Trigger closed_won transitions (fires webhooks realistically)
    await step_trigger_won(crm_url)

    # 6. Seed remaining deals via API webhook
    await step_seed_remaining(api_url)

    # Wait for last graph generation to complete
    print("\n⏳ Waiting 30 seconds for final graph generation...")
    await asyncio.sleep(30)

    # 7. Verify
    step_verify()

    print("\n" + "=" * 60)
    print("  🎉 SEEDING COMPLETE — Synapse is fully operational!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synapse Full End-to-End Seeding")
    parser.add_argument("--api_url", default=DEFAULT_API_URL)
    parser.add_argument("--crm_url", default=DEFAULT_CRM_URL)
    parser.add_argument("--hub_url", default=DEFAULT_HUB_URL)
    parser.add_argument("--graph_url", default=DEFAULT_GRAPH_URL)
    args = parser.parse_args()

    asyncio.run(main(args.api_url, args.crm_url, args.hub_url, args.graph_url))
