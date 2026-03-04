import sys
from pathlib import Path
from google.cloud import storage

sys.path.append(str(Path(__file__).parent.parent))
from core.config import config

def upload_pdfs():
    print(f"Uploading PDFs to gs://{config.uploads_bucket}/contracts/")
    client = storage.Client(project=config.project_id)
    bucket = client.bucket(config.uploads_bucket)
    
    contracts_dir = Path(__file__).parent.parent / "crm-simulator" / "uploads" / "contracts"
    if not contracts_dir.exists():
        print("Contracts directory not found!")
        return
        
    for pdf_file in contracts_dir.glob("*.pdf"):
        blob = bucket.blob(f"contracts/{pdf_file.name}")
        print(f"Uploading {pdf_file.name}...")
        blob.upload_from_filename(str(pdf_file))
        
    print("PDF upload complete!")

if __name__ == "__main__":
    upload_pdfs()
