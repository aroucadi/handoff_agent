
from google.cloud import firestore
import json

def verify_stages():
    db = firestore.Client(project="synapse-gemini-live")
    
    print("Verifying stages for key accounts...")
    accounts = ["PrecisionMetal Ltd", "RetailGiant Corp", "BioSynth Labs"]
    
    for account in accounts:
        # Convert account name to ID as likely stored
        client_id_prefix = account.lower().replace(" ", "-").replace(",", "").replace(".", "")
        graphs = db.collection("knowledge_graphs").stream()
        for graph in graphs:
            if client_id_prefix in graph.id:
                print(f"\nAccount: {account} (Graph ID: {graph.id})")
                entities = db.collection("knowledge_graphs").document(graph.id).collection("entities").where("type", "==", "Deal").stream()
                for entity in entities:
                    props = entity.to_dict().get("properties", {})
                    print(f"  Deal: {props.get('deal_id')} | Stage: {props.get('stage')}")

if __name__ == "__main__":
    verify_stages()
