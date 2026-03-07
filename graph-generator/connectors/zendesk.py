from __future__ import annotations
import httpx
from .base import BaseConnector

class ZendeskConnector(BaseConnector):
    """Connector for Zendesk Help Center (Guide) articles."""
    
    async def fetch_pages(self, uri: str, config: dict = None) -> list[dict]:
        """Fetch articles from Zendesk Help Center.
        URI should be the base domain, e.g., https://subdomain.zendesk.com
        """
        base_url = uri.rstrip('/')
        locale = (config or {}).get("locale", "en-us")
        articles_url = f"{base_url}/api/v2/help_center/{locale}/articles.json"
        
        pages = []
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.get(articles_url)
                resp.raise_for_status()
                data = resp.json()
            
            for article in data.get("articles", []):
                if article.get("draft"):
                    continue
                    
                pages.append({
                    "url": article.get("html_url"),
                    "title": article.get("title"),
                    "category": "zendesk",
                    "text_content": article.get("body", "")
                })
                
            from bs4 import BeautifulSoup
            for p in pages:
                soup = BeautifulSoup(p["text_content"], "html.parser")
                p["text_content"] = soup.get_text(separator="\n", strip=True)

        except Exception as e:
            print(f"[ZENDESK] Error fetching {uri}: {e}")
            
        return pages
