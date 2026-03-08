import asyncio
import httpx
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Mocking the discovery logic from website.py
async def test_sitemap_discovery(uri: str):
    parsed_start = urlparse(uri)
    start_domain = parsed_start.netloc
    start_path_boundary = parsed_start.path.rsplit('/', 1)[0] + '/' if '/' in parsed_start.path else '/'
    
    sitemap_urls = [
        f"{parsed_start.scheme}://{start_domain}/sitemap.xml",
        f"{parsed_start.scheme}://{start_domain}{start_path_boundary.rstrip('/')}/sitemap.xml" if start_path_boundary != '/' else None
    ]
    
    print(f"Testing URI: {uri}")
    print(f"Domain: {start_domain}")
    print(f"Path Boundary: {start_path_boundary}")
    print(f"Sitemap URLs to check: {list(filter(None, sitemap_urls))}")
    
    # In a real test we'd use httpx to fetch the local file if we had a server running,
    # but for this verification we just check the path logic.
    
    sitemap_path = "knowledge-center/sitemap.xml"
    with open(sitemap_path, "r") as f:
        content = f.read()
        soup = BeautifulSoup(content, "xml")
        locs = [loc.get_text(strip=True) for loc in soup.find_all("loc")]
        print(f"Parsed {len(locs)} URLs from sitemap.xml")
        
        for loc_url in locs:
            p_loc = urlparse(loc_url)
            is_valid = p_loc.netloc == "synapse-knowledge.storage.googleapis.com" and p_loc.path.startswith("/knowledge-center/")
            print(f"  [{'VALID' if is_valid else 'INVALID'}] {loc_url}")

if __name__ == "__main__":
    uri = "https://synapse-knowledge.storage.googleapis.com/knowledge-center/index.html"
    asyncio.run(test_sitemap_discovery(uri))
