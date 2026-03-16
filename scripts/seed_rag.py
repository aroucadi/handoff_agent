"""RAG Seeding Script for Synapse.

Iterates through ALL deals in seed_data.py and triggers the Synapse
Graph Generator webhook to build deal-centric knowledge graphs.

Each deal gets its own graph. Historical deals from the same account
are included as supplementary context within each deal's graph payload.
"""

import asyncio
import httpx
import argparse
from datetime import date
import sys
from pathlib import Path

# Add root to sys path
sys.path.append(str(Path(__file__).parent.parent))

# Add crm-simulator to path
crm_sim_path = Path(__file__).parent.parent / "crm-simulator"
sys.path.append(str(crm_sim_path))

from core.config import config
from seed_data import DEMO_DEALS

import os

# The Synapse API endpoint for CRM webhooks (remote default)
DEFAULT_WEBHOOK_BASE = "AUTO"
WEBHOOK_URL = os.environ.get("SYNAPSE_WEBHOOK_URL")


async def seed_rag(tenant_id: str = "default-tenant", lite: bool = False):
    # Group deals by company for historical context
    companies: dict[str, list] = {}
    for deal in DEMO_DEALS:
        if deal.company_name not in companies:
            companies[deal.company_name] = []
        companies[deal.company_name].append(deal)

    deals_to_process = DEMO_DEALS[:3] if lite else DEMO_DEALS
    total_deals = len(deals_to_process)
    
    print(f"Starting RAG seeding for tenant: {tenant_id}")
    print(f"Stats: {total_deals} deals across {len(set(d.company_name for d in deals_to_process))} accounts")
    if lite:
        print("⚠️ LITE MODE ACTIVE: Processing restricted to 3 deals.")
    print("🔒 ANTI-SUSPENSION MODE: Active. Delays of 15-25s enforced between all API calls.")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        for idx, deal in enumerate(deals_to_process, 1):
            # Build historical context: all OTHER deals for the same account
            account_deals = companies[deal.company_name]
            historical_deals = []
            for other_deal in account_deals:
                if other_deal.deal_id != deal.deal_id:
                    historical_deals.append({
                        "deal_id": other_deal.deal_id,
                        "stage": other_deal.stage.value,
                        "deal_value": other_deal.deal_value,
                        "close_date": str(other_deal.close_date) if other_deal.close_date else None,
                        "products": [{"name": p.name, "annual_value": p.annual_value} for p in other_deal.products],
                        "risks": [{"description": r.description, "severity": r.severity} for r in other_deal.risks],
                        "contacts": [{"name": c.name, "title": c.title, "role": c.role} for c in other_deal.contacts],
                    })

            print(f"\n[{idx}/{total_deals}] {deal.deal_id} — {deal.company_name}")
            print(f"    Stage: {deal.stage.value} | Value: ${deal.deal_value:,.0f} | Historical: {len(historical_deals)} deals")

            # Construct payload
            payload = {
                "tenant_id": tenant_id,
                "deal_id": deal.deal_id,
                "company_name": deal.company_name,
                "deal_value": deal.deal_value,
                "industry": deal.industry,
                "employee_count": deal.employee_count,
                "close_date": deal.close_date.isoformat() if deal.close_date else None,
                "sla_days": deal.sla_days,
                "products": [{"name": p.name, "annual_value": p.annual_value} for p in deal.products],
                "contacts": [
                    {
                        "name": c.name,
                        "title": c.title,
                        "role": c.role,
                        "pain_point": c.pain_point,
                        "commitment": c.commitment,
                    }
                    for c in deal.contacts
                ],
                "risks": [{"description": r.description, "severity": r.severity, "source": r.source} for r in deal.risks],
                "success_metrics": [
                    {
                        "metric": m.metric,
                        "current_value": m.current_value,
                        "target_value": m.target_value,
                        "timeframe": m.timeframe,
                    }
                    for m in deal.success_metrics
                ],
                "sales_transcript": deal.sales_transcript or "",
                "contract_pdf_url": f"gs://{config.uploads_bucket}/contracts/{deal.deal_id}_contract.pdf",
                "historical_deals": historical_deals,
            }

            try:
                resp = await client.post(WEBHOOK_URL, json=payload, timeout=30.0)
                if resp.status_code in [200, 202]:
                    msg = resp.json().get("message") or "Accepted"
                    print(f"    ✅ {msg}")
                else:
                    print(f"    ❌ Failed ({resp.status_code}): {resp.text[:120]}")
            except Exception as e:
                print(f"    ❌ Error: {str(e)}")

            # Anti-Suspension: mandatory throttled delay (15-25s) between RAG seeding payloads.
            import random
            wait_time = 15 + random.uniform(5.0, 10.0)
            print(f"    ⏳ Anti-Suspension: Sleeping {wait_time:.1f}s for Gemini/Vertex AI safety...")
            await asyncio.sleep(wait_time)

    print("\n" + "=" * 60)
    print(f"RAG seeding complete for tenant: {tenant_id}")
    print("Note: Graph generation is async. Check Firestore skill_graphs collection for status.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed RAG data for a specific tenant.")
    parser.add_argument("--tenant", type=str, default="default-tenant", help="The tenant_id to seed for.")
    parser.add_argument("--lite", action="store_true", help="Limit to 3 deals and add delays to prevent API abuse.")
    args = parser.parse_args()
    
    # Resolve webhook URL if not provided
    global WEBHOOK_URL
    if not WEBHOOK_URL:
        base_url = config.resolve_run_url("synapse-api")
        if not base_url:
            print("❌ Error: Could not resolve Synapse API URL for RAG seeding. Provide SYNAPSE_WEBHOOK_URL env var.")
            sys.exit(1)
        WEBHOOK_URL = f"{base_url.rstrip('/')}/api/webhooks/crm/deal-closed"

    asyncio.run(seed_rag(args.tenant, lite=args.lite))
