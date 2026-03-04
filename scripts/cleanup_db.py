import sys
from pathlib import Path

# Add core to path
sys.path.append(str(Path(__file__).parent.parent))

from google.cloud import firestore, storage
from core.config import config

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(f"Deleting {doc.reference.path}")
        # Delete any subcollections recursively
        for sub_coll in doc.reference.collections():
            delete_collection(sub_coll, batch_size)
            
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


def clean_gcs_bucket(bucket_name: str, prefix: str = ""):
    """Delete all objects in a GCS bucket under a given prefix."""
    gcs = storage.Client(project=config.project_id)
    bucket = gcs.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=prefix))
    if not blobs:
        print(f"  (empty)")
        return
    for blob in blobs:
        blob.delete()
    print(f"  Deleted {len(blobs)} objects")


def main():
    print(f"Starting full cleanup for project: {config.project_id}")
    print("=" * 60)
    db = firestore.Client(project=config.project_id)
    
    # 1. Firestore collections
    collections = [
        "notifications",
        "skill_graphs",
        "agent_traces",
        "sessions",
        "client_insights",
    ]
    
    print("\n[1/3] Purging Firestore collections...")
    for coll in collections:
        print(f"  Purging: {coll}")
        coll_ref = db.collection(coll)
        delete_collection(coll_ref, 100)

    # 2. GCS graph data
    print(f"\n[2/3] Purging GCS graph data: {config.skill_graphs_bucket}")
    clean_gcs_bucket(config.skill_graphs_bucket, prefix="clients/")

    # 3. GCS contract PDFs
    print(f"\n[3/3] Purging GCS contract PDFs: {config.uploads_bucket}")
    clean_gcs_bucket(config.uploads_bucket, prefix="contracts/")
        
    print("\n" + "=" * 60)
    print("Full cleanup complete! Firestore + GCS wiped.")

if __name__ == "__main__":
    main()

