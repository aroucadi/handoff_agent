"""Synapse Hub — Seeding Script.

Initializes the Hub's Firestore database with a default tenant configuration
and points the webhook_url to the newly deployed Graph Generator.
"""

import sys
import os
import argparse
from pathlib import Path
from google.cloud import firestore

# Add root to sys path for core.config
sys.path.append(str(Path(__file__).parent.parent))
from core.config import config

def seed_hub(tenant_id: str, graph_gen_url: str, crm_url: str):
    db = firestore.Client(project=config.project_id)
    TENANTS_COLLECTION = "tenants"

    print(f"Seeding Hub for project: {config.project_id}")
    print(f"Target Tenant: {tenant_id}")
    print(f"Graph Gen URL: {graph_gen_url}")
    print(f"CRM URL:       {crm_url}")

    # Normalize URL (append /generate if not present, though Hub expects the base usually)
    if not graph_gen_url.endswith("/generate"):
        webhook_url = f"{graph_gen_url.rstrip('/')}/generate"
    else:
        webhook_url = graph_gen_url

    tenant_data = {
        "tenant_id": tenant_id,
        "name": "Global Manufacturing Corp (Demo)",
        "brand_name": "ClawdView",
        "status": "active",
        "webhook_url": webhook_url,
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
                "contract_pdf_url": "contract_pdf_url"
            }
        },
        "products": [
            {"product_id": "prod-agile", "name": "ClawdView AgilePlace", "description": "Agile project management", "node_id": "clawdview-agileplace", "knowledge_generated": True},
            {"product_id": "prod-port", "name": "ClawdView Portfolios", "description": "Strategic portfolio management", "node_id": "clawdview-portfolios", "knowledge_generated": True},
            {"product_id": "prod-hub", "name": "ClawdView Hub", "description": "Integration and ETL hub", "node_id": "clawdview-hub", "knowledge_generated": True},
            {"product_id": "prod-ppm", "name": "ClawdView PPM Pro", "description": "Project and Portfolio management", "node_id": "clawdview-ppm-pro", "knowledge_generated": True}
        ],
        "agent": {
            "roles": ["csm", "sales", "support", "win-back"],
            "persona": "Professional, data-driven, and proactive enterprise assistant.",
            "brand_name": "Synapse"
        },
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP
    }

    doc_ref = db.collection(TENANTS_COLLECTION).document(tenant_id)
    doc_ref.set(tenant_data)
    
    print(f"✅ Hub tenant '{tenant_id}' successfully seeded.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Hub tenant configuration.")
    parser.add_argument("--tenant", type=str, default="default-tenant", help="The tenant_id to seed.")
    parser.add_argument("--url", type=str, required=True, help="The Graph Generator URL.")
    parser.add_argument("--crm_url", type=str, required=True, help="The CRM Simulator URL.")
    args = parser.parse_args()
    
    seed_hub(args.tenant, args.url, args.crm_url)
