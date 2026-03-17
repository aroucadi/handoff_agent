
from google.cloud import firestore
import json
from datetime import datetime

# Define valid stages based on DealStage enum if possible, or fallback to known good ones
VALID_STAGES = [
    "prospecting", "qualification", "discovery", "value_proposition", 
    "negotiation", "closed_won", "closed_lost", "implemented"
]

def fix_deal_stages():
    db = firestore.Client(project="synapse-gemini-live")
    
    collections_to_check = ["knowledge_graphs", "skill_graphs"]
    total_fixed = 0

    for coll_name in collections_to_check:
        print(f"\nChecking collection: {coll_name}...")
        graphs = db.collection(coll_name).stream()
        
        for graph in graphs:
            # For knowledge_graphs, deals are in the 'entities' subcollection
            if coll_name == "knowledge_graphs":
                entities = db.collection(coll_name).document(graph.id).collection("entities").where("type", "==", "Deal").stream()
                for entity in entities:
                    data = entity.to_dict()
                    props = data.get("properties", {})
                    stage = props.get("stage")
                    
                    if not stage or stage.lower() == "unknown":
                        # Attempt to derive stage from deal_id if it follows our naming convention
                        deal_id = props.get("deal_id", "").upper()
                        new_stage = "prospecting" # Default
                        
                        if deal_id.startswith("WON") or deal_id.startswith("IMP"):
                            new_stage = "closed_won"
                        elif deal_id.startswith("LOST"):
                            new_stage = "closed_lost"
                        elif deal_id.startswith("OPP"):
                            new_stage = "negotiation"
                            
                        print(f"  [FIX] {coll_name}/{graph.id}/entities/{entity.id}: stage '{stage}' -> '{new_stage}'")
                        props["stage"] = new_stage
                        props["last_fixed_at"] = datetime.utcnow().isoformat()
                        entity.reference.update({"properties": props})
                        total_fixed += 1
            
            # For skill_graphs, deals are in the 'nodes' subcollection
            elif coll_name == "skill_graphs":
                nodes = db.collection(coll_name).document(graph.id).collection("nodes").stream()
                for node in nodes:
                    data = node.to_dict()
                    # skill_graphs nodes have properties at the top level or in metadata
                    # and often represent deals if the node_id ends in '_deal'
                    if node.id.endswith("_deal"):
                        stage = data.get("stage")
                        if not stage or (isinstance(stage, list) and "unknown" in [s.lower() for s in stage]):
                            deal_id = data.get("deal_id", "").upper()
                            new_stage = "prospecting"
                            if deal_id.startswith("WON") or deal_id.startswith("IMP"):
                                new_stage = "closed_won"
                            elif deal_id.startswith("LOST"):
                                new_stage = "closed_lost"
                            
                            print(f"  [FIX] {coll_name}/{graph.id}/nodes/{node.id}: stage '{stage}' -> '{new_stage}'")
                            # skill_graphs uses list for stage sometimes
                            node.reference.update({"stage": [new_stage], "last_fixed_at": datetime.utcnow().isoformat()})
                            total_fixed += 1

    print(f"\nFinished. Total deals fixed: {total_fixed}")

if __name__ == "__main__":
    fix_deal_stages()
