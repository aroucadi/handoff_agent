"""Graph Generator — Knowledge Center Extractor.

Crawls the ClawdView Knowledge Center static site and extracts
Product, Feature, UseCase, KBArticle, Limitation, and Integration
entities with their connecting edges.

This runs as a one-time or periodic batch job to populate the
product knowledge layer of the graph.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.config import config
from core.llm import generate_content_with_fallback
from google.genai.types import GenerateContentConfig
from ontology import get_extraction_schema_prompt


# ── Static file crawler ─────────────────────────────────────────

def crawl_knowledge_center(kc_dir: str | Path) -> list[dict]:
    """Crawl HTML files from the knowledge center directory.

    Args:
        kc_dir: Path to the knowledge-center/ directory.

    Returns:
        List of dicts with "url", "title", "category", "text_content".
    """
    kc_path = Path(kc_dir)
    pages = []

    for html_file in kc_path.rglob("*.html"):
        # Skip index pages for entity extraction (they're just navigation)
        if html_file.name == "index.html" and html_file.parent == kc_path:
            continue

        relative_path = html_file.relative_to(kc_path)
        category = relative_path.parts[0] if len(relative_path.parts) > 1 else "general"

        with open(html_file, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Extract clean text from the main content area
        main = soup.find("main") or soup.find("body")
        if not main:
            continue

        # Remove nav and footer
        for tag in main.find_all(["header", "footer", "nav"]):
            tag.decompose()

        title = soup.find("title")
        title_text = title.get_text(strip=True) if title else html_file.stem

        text = main.get_text(separator="\n", strip=True)

        pages.append({
            "url": str(relative_path).replace("\\", "/"),
            "title": title_text.split("—")[0].strip(),
            "category": category,
            "text_content": text,
        })

    print(f"[KC CRAWLER] Found {len(pages)} pages in {kc_path}")
    return pages


# ── Gemini entity extraction ────────────────────────────────────

KC_EXTRACTION_PROMPT = """You are an expert at extracting structured knowledge from product documentation.

Given a product documentation page, extract ALL entities and relationships following this ontology:

{schema}

IMPORTANT RULES:
- Extract ONLY entities explicitly described in the text
- Each entity must have a unique "id" in snake_case (e.g., "product_clawdview_portfolios")
- Use the exact node type names from the ontology
- Create edges BETWEEN entities you extract (e.g., Product → Feature, Feature → Limitation)
- For Products: include name, version, category, tier, description
- For Features: include name, description, maturity, scaling_notes
- For UseCases: include title, description, industry_applicability
- For Limitations: include description, severity, workaround
- For Integrations: include partner_system, sync_type, data_flow
- For KBArticle: the page itself is one KB article — create it

Return ONLY valid JSON with this structure:
{{
  "nodes": [
    {{"id": "unique_id", "type": "NodeTypeName", "properties": {{...}}}}
  ],
  "edges": [
    {{"type": "EDGE_TYPE", "from_id": "node_id", "to_id": "node_id", "properties": {{}}}}
  ]
}}

DOCUMENT:
Title: {title}
Category: {category}
URL: {url}

Content:
{content}
"""


async def extract_entities_from_page(page: dict) -> dict | None:
    """Extract entities and relationships from a single KC page using Gemini.

    Args:
        page: Dict with "url", "title", "category", "text_content".

    Returns:
        Dict with "nodes" and "edges", or None on failure.
    """
    schema = get_extraction_schema_prompt()

    prompt = KC_EXTRACTION_PROMPT.format(
        schema=schema,
        title=page["title"],
        category=page["category"],
        url=page["url"],
        content=page["text_content"][:6000],  # Limit input to fit context window
    )

    try:
        gen_config = GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.5, # Slightly higher temperature is often recommended for thinking models
            max_output_tokens=8192
        )

        raw_text = await generate_content_with_fallback(
            contents=[prompt],
            gen_config=gen_config,
            primary_model=config.gen_model,
            fallback_model=config.fallback_model,
        )

        if not raw_text:
            return None

        result = json.loads(raw_text)

        # Also add the page itself as a KBArticle node
        kb_id = f"kb_{page['url'].replace('/', '_').replace('.html', '')}"
        kb_exists = any(n["id"] == kb_id for n in result.get("nodes", []))
        if not kb_exists:
            result.setdefault("nodes", []).append({
                "id": kb_id,
                "type": "KBArticle",
                "properties": {
                    "title": page["title"],
                    "category": page["category"],
                    "url": page["url"],
                    "summary": page["text_content"][:200],
                    "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                },
            })

        print(f"[KC EXTRACT] {page['title']}: {len(result.get('nodes', []))} nodes, {len(result.get('edges', []))} edges")
        return result

    except json.JSONDecodeError as e:
        print(f"[KC EXTRACT] JSON parse error for {page['title']}: {e}")
        return None
    except Exception as e:
        print(f"[KC EXTRACT] Error extracting {page['title']}: {e}")
        return None


async def extract_all_knowledge_center(kc_dir: str | Path) -> dict:
    """Crawl and extract all entities from the Knowledge Center.

    Returns:
        Merged dict with all "nodes" and "edges" from all pages.
    """
    pages = crawl_knowledge_center(kc_dir)

    all_nodes = []
    all_edges = []
    seen_ids = set()

    import asyncio
    sem = asyncio.Semaphore(4)

    async def _safe_extract(page):
        async with sem:
            return await extract_entities_from_page(page)

    results = await asyncio.gather(*[_safe_extract(p) for p in pages])

    for result in results:
        if result:
            for node in result.get("nodes", []):
                if node["id"] not in seen_ids:
                    all_nodes.append(node)
                    seen_ids.add(node["id"])
            all_edges.extend(result.get("edges", []))

    print(f"[KC EXTRACT] Total: {len(all_nodes)} unique nodes, {len(all_edges)} edges from {len(pages)} pages")
    return {"nodes": all_nodes, "edges": all_edges}
