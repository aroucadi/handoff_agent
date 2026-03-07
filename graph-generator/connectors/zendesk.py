from __future__ import annotations
import requests
from .base import BaseConnector

class ZendeskConnector(BaseConnector):
    """Connector for Zendesk Help Center (Guide) articles."""
    
    async def fetch_pages(self, uri: str, config: dict = None) -> list[dict]:
        """Fetch articles from Zendesk Help Center.
        URI should be the base domain, e.g., https://subdomain.zendesk.com
        """
        base_url = uri.rstrip('/')
        articles_url = f"{base_url}/api/v2/help_center/en-us/articles.json"
        
        pages = []
        try:
            # Note: Enterprise use usually requires API keys, but public help centers 
            # often allow unauthenticated list if configured to do so.
            # We'll support basic fetch for now.
            resp = requests.get(articles_url, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            
            for article in data.get("articles", []):
                if article.get("draft"):
                    continue
                    
                pages.append({
                    "url": article.get("html_url"),
                    "title": article.get("title"),
                    "category": "zendesk",
                    "text_content": article.get("body", "") # Note: body contains HTML
                })
                
            # Handle HTML in body if needed (strip tags)
            from bs4 import BeautifulSoup
            for p in pages:
                soup = BeautifulSoup(p["text_content"], "html.parser")
                p["text_content"] = soup.get_text(separator="\n", strip=True)

        except Exception as e:
            print(f"[ZENDESK] Error fetching {uri}: {e}")
            
        return pages
