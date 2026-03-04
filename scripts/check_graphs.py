"""Quick Firestore graph checker."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from google.cloud import firestore

db = firestore.Client(project="synapse-488201")
graphs = list(db.collection("skill_graphs").stream())
print(f"Total graphs: {len(graphs)}")
for g in graphs:
    data = g.to_dict()
    status = data.get("status", "?")
    node_count = data.get("node_count", 0)
    print(f"  {g.id}: status={status}, nodes={node_count}")

notifs = list(db.collection("notifications").stream())
print(f"\nNotifications: {len(notifs)}")
for n in notifs:
    d = n.to_dict()
    print(f"  {d.get('type','?')}: {d.get('message', d.get('title','?'))[:80]}")
