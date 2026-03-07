from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .base import BaseConnector

class WebsiteConnector(BaseConnector):
    """Connector for crawling public websites and sitemaps."""
    
    async def fetch_pages(self, uri: str, config: dict = None) -> list[dict]:
        max_pages = (config or {}).get("max_pages", 15)
        pages = []
        visited = set()
        queue = [uri]
        
        parsed_start = urlparse(uri)
        start_domain = parsed_start.netloc
        start_path_boundary = parsed_start.path.rsplit('/', 1)[0] + '/' if '/' in parsed_start.path else '/'

        while queue and len(pages) < max_pages:
            current_uri = queue.pop(0)
            if current_uri in visited:
                continue
            visited.add(current_uri)
            try:
                # We use sync requests for now to maintain parity with legacy logic, 
                # but could upgrade to httpx/playwright later
                resp = requests.get(current_uri, timeout=15)
                resp.raise_for_status()

                if 'text/html' not in resp.headers.get('Content-Type', ''):
                    continue

                soup = BeautifulSoup(resp.content, "html.parser")
                main = soup.find("main") or soup.find("body") or soup
                for tag in main.find_all(["header", "footer", "nav"]):
                    tag.decompose()

                title = soup.find("title")
                title_text = title.get_text(strip=True) if title else current_uri.split("/")[-1]
                text = main.get_text(separator="\n", strip=True)

                if text:
                    pages.append({
                        "url": current_uri,
                        "title": title_text,
                        "category": "web",
                        "text_content": text
                    })

                for a_tag in soup.find_all("a", href=True):
                    next_uri = urljoin(current_uri, a_tag['href']).split('#')[0]
                    parsed_next = urlparse(next_uri)
                    if parsed_next.netloc == start_domain and parsed_next.path.startswith(start_path_boundary) and next_uri not in visited:
                        queue.append(next_uri)
            except Exception:
                continue

        return pages
