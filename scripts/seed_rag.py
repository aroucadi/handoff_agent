"""RAG Seeding Script for Synapse.

Iterates through Closed Won deals in seed_data.py and triggers the Synapse 
Graph Generator webhook to build historical knowledge graphs.
"""

import asyncio
import httpx
from datetime import date
import sys
from pathlib import Path

# Add crm-simulator to path
crm_sim_path = Path(__file__).parent.parent / "crm-simulator"
sys.path.append(str(crm_sim_path))

from core.config import config
from seed_data import DEMO_DEALS

# The Synapse API endpoint for CRM webhooks
WEBHOOK_URL = "https://synapse-api-uicugotuta-uc.a.run.app/api/webhooks/crm/deal-closed"

async def seed_rag():
    print(f"🚀 Starting RAG seeding for {len(DEMO_DEALS)} potential deals...")
    
    async with httpx.AsyncClient() as client:
        for deal in DEMO_DEALS:
            print(f"📦 Seeding deal: {deal.company_name} ({deal.deal_id}) Stage: {deal.stage}")
            
            # Construct payload
            payload = {
                    "deal_id": deal.deal_id,
                    "company_name": deal.company_name,
                    "deal_value": deal.deal_value,
                    "industry": deal.industry,
                    "close_date": deal.close_date.isoformat() if deal.close_date else None,
                    "products": [{"name": p.name, "annual_value": p.annual_value} for p in deal.products],
                    "contacts": [{"name": c.name, "title": c.title, "role": c.role} for c in deal.contacts],
                    "risks": [{"description": r.description, "severity": r.severity} for r in deal.risks],
                    "sales_transcript": deal.sales_transcript or "Standard historical win: customer migrated to Synapse for unified sales orchestration.",
                    "contract_pdf_url": f"gs://{config.uploads_bucket}/contracts/{deal.deal_id}.pdf"
                }
                
            try:
                resp = await client.post(WEBHOOK_URL, json=payload, timeout=30.0)
                if resp.status_code in [200, 202]:
                    msg = resp.json().get('message') or "Ingestion job started (Async)"
                    print(f"   ✅ Success: {msg}")
                else:
                    print(f"   ❌ Failed ({resp.status_code}): {resp.text}")
            except Exception as e:
                print(f"   ⚠️ Error: {str(e)}")
                    
    print("\n✨ RAG seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_rag())
