from __future__ import annotations
from google.cloud import storage as gcs
from .base import BaseConnector

class GcsConnector(BaseConnector):
    """Connector for scraping HTML/Documents from GCS buckets."""
    
    async def fetch_pages(self, uri: str, config: dict = None) -> list[dict]:
        from bs4 import BeautifulSoup
        
        raw = uri.replace("gs://", "", 1)
        parts = raw.split("/", 1)
        bucket_name = parts[0]
        prefix = parts[1].rstrip("/") + "/" if len(parts) > 1 and parts[1] else ""
        
        client = gcs.Client()
        bucket = client.bucket(bucket_name)
        pages: list[dict] = []

        for blob in bucket.list_blobs(prefix=prefix):
            if not blob.name.endswith(".html"):
                continue

            relative_path = blob.name[len(prefix):]
            if relative_path == "index.html":
                continue

            parts = relative_path.split("/")
            category = parts[0] if len(parts) > 1 else "general"

            html = blob.download_as_text(encoding="utf-8")
            soup = BeautifulSoup(html, "html.parser")

            main = soup.find("main") or soup.find("body")
            if not main:
                continue

            for tag in main.find_all(["header", "footer", "nav"]):
                tag.decompose()

            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else parts[-1].replace(".html", "")

            text = main.get_text(separator="\n", strip=True)
            pages.append({
                "url": f"gs://{bucket_name}/{blob.name}",
                "title": title_text.split("—")[0].strip(),
                "category": category,
                "text_content": text,
            })

        return pages
