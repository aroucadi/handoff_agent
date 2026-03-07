from __future__ import annotations
import requests
import io
import PyPDF2
from .base import BaseConnector

class DocumentConnector(BaseConnector):
    """Connector for direct PDF/Markdown file ingestion."""
    
    async def fetch_pages(self, uri: str, config: dict = None) -> list[dict]:
        if uri.lower().endswith(".pdf"):
            return await self._fetch_pdf(uri)
        elif uri.lower().endswith(".md"):
            return await self._fetch_md(uri)
        return []

    async def _fetch_pdf(self, uri: str) -> list[dict]:
        resp = requests.get(uri, timeout=15)
        resp.raise_for_status()
        reader = PyPDF2.PdfReader(io.BytesIO(resp.content))
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        return [{
            "url": uri,
            "title": uri.split("/")[-1],
            "category": "document",
            "text_content": text
        }]

    async def _fetch_md(self, uri: str) -> list[dict]:
        resp = requests.get(uri, timeout=15)
        resp.raise_for_status()
        return [{
            "url": uri,
            "title": uri.split("/")[-1],
            "category": "document",
            "text_content": resp.text
        }]
