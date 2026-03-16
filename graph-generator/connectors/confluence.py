from __future__ import annotations
import httpx
from .base import BaseConnector

class ConfluenceConnector(BaseConnector):
    """Connector for Confluence Cloud/Server pages."""
    
    async def fetch_pages(self, uri: str, config: dict = None) -> list[dict]:
        """Fetch pages from Confluence.
        URI should be the base domain, e.g., https://sitename.atlassian.net
        Requires space key in config.
        """
        space_key = (config or {}).get("space_key")
        if not space_key:
            print("[CONFLUENCE] No space_key provided in config")
            return []
            
        base_url = uri.rstrip('/')
        api_url = f"{base_url}/wiki/rest/api/content?spaceKey={space_key}&expand=body.storage"
        
        pages = []
        try:
            headers = {}
            auth_token = (config or {}).get("auth_token")
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
                
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.get(api_url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            
            for item in data.get("results", []):
                pages.append({
                    "url": f"{base_url}/wiki{item.get('_links', {}).get('webui')}",
                    "title": item.get("title"),
                    "category": "confluence",
                    "text_content": item.get("body", {}).get("storage", {}).get("value", "") # In HTML
                })
                
            from bs4 import BeautifulSoup
            for p in pages:
                soup = BeautifulSoup(p["text_content"], "html.parser")
                p["text_content"] = soup.get_text(separator="\n", strip=True)

        except Exception as e:
            print(f"[CONFLUENCE] Error fetching space {space_key} from {uri}: {e}")
            
        return pages
