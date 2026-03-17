import os
from google.cloud import firestore

def check_graph():
    db = firestore.Client(project="synapse-gemini-live")
    client_id = "9049d8ec_retailgiant-corp"
    
    print(f"Checking graph for: {client_id}")
    
    # Check status doc
    status_ref = db.collection("knowledge_graphs").document(client_id)
    status_doc = status_ref.get()
    if status_doc.exists:
        print(f"Status: {status_doc.to_dict()}")
    else:
        print("Status document NOT FOUND")
        
    # Check entities
    entities_ref = status_ref.collection("entities")
    entities = list(entities_ref.stream())
    print(f"Entities count: {len(entities)}")
    for e in entities[:5]:
        print(f"  - Entity: {e.id}, Type: {e.to_dict().get('type')}")
        
    # Check edges
    edges_ref = status_ref.collection("edges")
    edges = list(edges_ref.stream())
    print(f"Edges count: {len(edges)}")
    for edge in edges[:5]:
        d = edge.to_dict()
        print(f"  - Edge: {d.get('from_id')} -> {d.get('type')} -> {d.get('to_id')}")

if __name__ == "__main__":
    check_graph()
