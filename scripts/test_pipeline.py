from __future__ import annotations

import argparse
import asyncio
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

import httpx
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# Add root directory to python path for shared modules
sys.path.append(str(Path(__file__).parent.parent))
from core.config import config
from core.db import get_firestore_client

async def _post_json(url: str, payload: dict | None = None, timeout: float = 30.0) -> dict:
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload or {})
        resp.raise_for_status()
        return resp.json()

async def delete_collection(coll_ref, batch_size=100):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0
    for doc in docs:
        for sub_coll in doc.reference.collections():
            await delete_collection(sub_coll, batch_size)
        doc.reference.delete()
        deleted += 1
    if deleted >= batch_size:
        await delete_collection(coll_ref, batch_size)

async def cleanup_test_data(db, tenant_id, deal_id, client_id):
    print(f"\nCleaning up test data for Deal {deal_id}...")
    
    # 1. Delete Graph Job
    jobs_query = db.collection("graph_jobs").where(filter=FieldFilter("deal_id", "==", deal_id))
    for job_doc in jobs_query.stream():
        print(f"  - Deleting Graph Job: {job_doc.id}")
        job_doc.reference.delete()
        
    # 2. Delete CRM Deal (in Firestore)
    deal_ref = db.collection("deals").document(tenant_id).collection("items").document(deal_id)
    if deal_ref.get().exists:
        print(f"  - Deleting CRM Deal: {deal_id}")
        deal_ref.delete()
        
    # 3. Delete Knowledge Graph (recursive)
    if client_id:
        kg_ref = db.collection("knowledge_graphs").document(client_id)
        if kg_ref.get().exists:
            print(f"  - Purging Knowledge Graph: {client_id}")
            for sub in kg_ref.collections():
                await delete_collection(sub)
            kg_ref.delete()
            
        sg_ref = db.collection("skill_graphs").document(client_id)
        if sg_ref.get().exists:
            print(f"  - Purging Skill Graph: {client_id}")
            for sub in sg_ref.collections():
                await delete_collection(sub)
            sg_ref.delete()

    # 4. Delete Test Tenant
    tenant_ref = db.collection("tenants").document(tenant_id)
    if tenant_ref.get().exists:
        print(f"  - Deleting Test Tenant: {tenant_id}")
        tenant_ref.delete()

async def run_integration_test(crm_url: str, graph_url: str, skip_cleanup: bool = False):
    print("Starting Headless Integration Test...")
    db = get_firestore_client()
    
    # 1. Create a Realistic Stealth Deal
    deal_id = f"STLTH-Q4-{uuid.uuid4().hex[:4].upper()}"
    tenant_id = "stealth-onboarding-123"
    company_name = f"StealthNode High-Tech {deal_id}"
    client_id = None
    
    try:
        # Ensure tenant exists in Firestore so ingest webhook doesn't 404
        db.collection("tenants").document(tenant_id).set({
            "tenant_id": tenant_id,
            "name": "StealthNode Integration Partner",
            "brand_name": "ClawdView",
            "webhook_secret": "",
            "crm": {
                "crm_type": "custom",
                "connected": True
            }
        })
        
        deal_payload = {
            "deal_id": deal_id,
            "company_name": company_name,
            "deal_value": 50000,
            "stage": "prospecting",
            "contacts": [{"name": "Jane Test", "title": "VP of Engineering", "role": "champion", "email": "jane@test.local"}],
            "products": [{"name": "ClawdView AgilePlace", "annual_value": 50000}],
            "sla_days": 14,
            "csm_id": "csm_stealth_001",
            "industry": "technology",
            "employee_count": 500,
            "risks": [],
            "success_metrics": [],
            "sales_transcript": "Customer wants to deploy quickly.",
            "tenant_id": tenant_id,
            "webhook_url": f"{graph_url.rstrip('/')}/ingest/{tenant_id}"
        }
        
        print(f"1. Creating Test Deal [{deal_id}] in CRM...")
        await _post_json(f"{crm_url}/api/deals", payload=deal_payload)
        
        print(f"2. Progressing Deal [{deal_id}] to CLOSED_WON...")
        await _post_json(f"{crm_url}/api/deals/{deal_id}/stage?stage=closed_won")
        
        print("3. Polling Firestore 'graph_jobs' Ledger for Graph Generator job...")
        max_retries = 30
        sleep_seconds = 2
        job_completed = False
        
        for attempt in range(max_retries):
            query = db.collection("graph_jobs").where(filter=FieldFilter("deal_id", "==", deal_id)).limit(1)
            docs = list(query.stream())
            
            if docs:
                job = docs[0].to_dict()
                found_job_id = job.get("job_id")
                status = job.get("status")
                print(f"   - Attempt {attempt+1}/{max_retries}: Found Job [{found_job_id}], Status: {status}")
                
                if status == "complete":
                    job_completed = True
                    client_id = job.get("client_id")
                    break
                elif status == "failed":
                    print(f"Job Failed! Error: {job.get('error')}")
                    return False
            else:
                print(f"   - Attempt {attempt+1}/{max_retries}: Job not found yet...")
                
            await asyncio.sleep(sleep_seconds)
            
        if not job_completed:
            print("Timeout waiting for Graph Generator job to complete.")
            return False
            
        print(f"Job Completed Successfully! Client ID: {client_id}")
        
        print("4. Verifying Knowledge Graph Nodes in Firestore...")
        coll_ref = db.collection("knowledge_graphs").document(client_id).collection("entities")
        nodes = list(coll_ref.limit(5).stream())
        
        if nodes:
            print(f"Verified: Found {len(nodes)} entities generated for {client_id}.")
        else:
            print(f"Verification Failed: No entities found for {client_id}.")
            return False
                
        print("Full Integration Test Passed!")
        return True

    finally:
        if not skip_cleanup:
            await cleanup_test_data(db, tenant_id, deal_id, client_id)
        else:
            print("\nSkipping cleanup as requested.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--crm_url", default="http://localhost:8001", help="CRM Simulator URL")
    parser.add_argument("--graph_url", default="http://localhost:8002", help="Graph Generator URL")
    parser.add_argument("--skip_cleanup", action="store_true", help="Skip purging test data from Firestore")
    args = parser.parse_args()
    
    success = asyncio.run(run_integration_test(args.crm_url, args.graph_url, args.skip_cleanup))
    if not success:
        sys.exit(1)
    sys.exit(0)
