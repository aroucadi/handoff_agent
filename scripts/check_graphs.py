import os
import subprocess
from google.cloud import firestore

# Auto-resolve project ID
try:
    result = subprocess.run(
        ["gcloud", "config", "get-value", "project"],
        capture_output=True, text=True, check=False, shell=True
    )
    project_id = result.stdout.strip()
except Exception:
    project_id = os.environ.get("PROJECT_ID", "synapse-gemini-live")

db = firestore.Client(project=project_id)
print(f"--- Firestore Check: {project_id} ---")

# 1. Check Graphs (Both collections)
for coll_name in ["knowledge_graphs", "skill_graphs"]:
    docs = list(db.collection(coll_name).stream())
    print(f"\nCollection '{coll_name}': {len(docs)} documents")
    for g in docs:
        data = g.to_dict()
        status = data.get("status", "?")
        # Support Phase 1B (entity_count) and Phase 1A (node_count)
        nodes = data.get("entity_count") or data.get("node_count")
        if nodes is None:
            # Fallback to subcollection count
            nodes = len(list(g.reference.collection("entities").stream())) or \
                    len(list(g.reference.collection("nodes").stream()))
        
        print(f"  - {g.id}: status={status}, nodes={nodes}")

# 2. Check Notifications
notifs = list(db.collection("notifications").stream())
print(f"\nNotifications: {len(notifs)}")
for n in notifs:
    d = n.to_dict()
    # Support new notification format
    status = d.get("status", "ready")
    company = d.get("company_name", "?")
    deal = d.get("deal_id", "?")
    print(f"  [{status.upper()}] {company} ({deal})")

# 3. Check Hub Tenant
tenants = list(db.collection("tenants").stream())
print(f"\nTenants: {len(tenants)}")
for t in tenants:
    d = t.to_dict()
    print(f"  - {d.get('name')} [{d.get('status')}] (ID: {t.id})")
