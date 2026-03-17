
from google.cloud import firestore
import json

def check_phase():
    db = firestore.Client(project="synapse-gemini-live")
    
    print("Checking knowledge_graphs collection...")
    docs = db.collection("knowledge_graphs").limit(5).stream()
    for doc in docs:
        data = doc.to_dict()
        print(f"Graph ID: {doc.id}")
        # Check entities in this graph
        entities = db.collection("knowledge_graphs").document(doc.id).collection("entities").where("type", "==", "Deal").limit(3).stream()
        for entity in entities:
            e_data = entity.to_dict()
            props = e_data.get("properties", {})
            print(f"  Deal Entity: {entity.id}")
            print(f"    Properties: {json.dumps(props, indent=2)}")
            if "phase" in props:
                print(f"    PHASE FOUND: {props['phase']}")
            else:
                print("    PHASE NOT FOUND")

if __name__ == "__main__":
    check_phase()
