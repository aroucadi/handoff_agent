"""Graph Generator — Firestore Indexing & Embedding Module.

Stores node metadata and vector embeddings in Firestore for search and traversal.
Uses gemini-embedding-001 for real vector embeddings.
"""

from __future__ import annotations

import re
import yaml
from datetime import datetime

from google import genai
from google.genai.types import EmbedContentConfig

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import config
from core.db import get_firestore_async_client as _get_firestore


def _parse_yaml_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (metadata dict, body text without frontmatter)
    """
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        metadata = {}

    body = parts[2].strip()
    return metadata, body


def _extract_wikilinks(content: str) -> list[str]:
    """Extract all [[wikilink]] node_ids from markdown content."""
    return re.findall(r'\[\[([^\]]+)\]\]', content)


async def generate_embedding(text: str) -> list[float]:
    """Generate a vector embedding using gemini-embedding-001.

    Args:
        text: Text to embed.

    Returns:
        List of float values (768 dimensions for hackathon config).
    """
    client = genai.Client(api_key=config.gemini_api_key)

    result = await client.aio.models.embed_content(
        model=config.embedding_model,
        contents=text,
        config=EmbedContentConfig(
            output_dimensionality=config.embedding_dims,
        ),
    )

    return result.embeddings[0].values


async def index_node(client_id: str, node_id: str, content: str) -> dict:
    """Index a single node in Firestore with metadata and embedding.

    Stores:
    - YAML frontmatter fields
    - Body text preview
    - Wikilink references
    - Vector embedding (768d via gemini-embedding-001)

    Args:
        client_id: Client identifier.
        node_id: Node identifier.
        content: Full markdown content.

    Returns:
        Firestore document data.
    """
    metadata, body = _parse_yaml_frontmatter(content)
    wikilinks = _extract_wikilinks(content)

    # Generate embedding from title + description + body (first 500 chars)
    embed_text = f"{metadata.get('title', node_id)} | {metadata.get('description', '')} | {body[:500]}"
    embedding = await generate_embedding(embed_text)

    doc_data = {
        "node_id": node_id,
        "client_id": client_id,
        "title": metadata.get("title", node_id),
        "layer": metadata.get("layer", "client"),
        "domain": metadata.get("domain", ""),
        "stage": metadata.get("stage", ["onboarding"]),
        "description": metadata.get("description", ""),
        "links": metadata.get("links", []),
        "wikilinks_in_body": wikilinks,
        "body_preview": body[:300],
        "word_count": len(body.split()),
        "embedding": embedding,
        "last_updated": metadata.get("last_updated", datetime.utcnow().isoformat()),
        "indexed_at": datetime.utcnow().isoformat(),
    }

    db = _get_firestore()
    doc_ref = db.collection("skill_graphs").document(client_id).collection("nodes").document(node_id)
    await doc_ref.set(doc_data)
    print(f"[FIRESTORE] Indexed: skill_graphs/{client_id}/nodes/{node_id}")

    return doc_data


async def index_all_nodes(client_id: str, nodes: list[dict], payload: dict = None) -> list[dict]:
    """Index all generated nodes in Firestore.

    Args:
        client_id: Client identifier.
        nodes: List of dicts with "node_id" and "content".
        payload: Original webhook payload containing CRM data.

    Returns:
        List of Firestore document data.
    """
    if payload is None:
        payload = {}
    indexed = []
    for node in nodes:
        node_id = node.get("node_id", "unknown")
        content = node.get("content", "")
        doc_data = await index_node(client_id, node_id, content)
        indexed.append(doc_data)

    # Also write the client-level status document
    db = _get_firestore()
    status_ref = db.collection("skill_graphs").document(client_id)

    # Use today + SLA days as a simple kickoff date calculation for the demo
    # In a real system this would be parsed accurately from the contract/CRM.
    kickoff_date = payload.get("close_date", datetime.utcnow().isoformat()[:10])

    await status_ref.set({
        "client_id": client_id,
        "company_name": payload.get("company_name", "Unknown Company"),
        "deal_value": payload.get("deal_value", 0),
        "kickoff_date": kickoff_date,
        "csm_id": payload.get("csm_id", "unknown"),
        "status": "ready",
        "node_count": len(indexed),
        "node_ids": [n["node_id"] for n in indexed],
        "generated_at": datetime.utcnow().isoformat(),
    })

    return indexed


async def get_graph_status(client_id: str) -> dict | None:
    """Get the generation status for a client's graph."""
    db = _get_firestore()
    doc_ref = db.collection("skill_graphs").document(client_id)
    doc = await doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None


async def search_by_embedding(client_id: str, query_embedding: list[float], top_k: int = 5) -> list[dict]:
    """Search for similar nodes using vector similarity.

    Uses cosine similarity against stored embeddings in Firestore.
    """
    db = _get_firestore()
    nodes_ref = db.collection("skill_graphs").document(client_id).collection("nodes")
    docs = nodes_ref.stream()

    # Calculate cosine similarity
    results = []
    async for doc in docs:
        data = doc.to_dict()
        stored_embedding = data.get("embedding", [])
        if not stored_embedding:
            continue

        # Cosine similarity
        dot = sum(a * b for a, b in zip(query_embedding, stored_embedding))
        norm_a = sum(a * a for a in query_embedding) ** 0.5
        norm_b = sum(b * b for b in stored_embedding) ** 0.5
        similarity = dot / (norm_a * norm_b) if norm_a and norm_b else 0

        results.append({
            "node_id": data.get("node_id"),
            "title": data.get("title"),
            "description": data.get("description"),
            "similarity": similarity,
            "body_preview": data.get("body_preview", ""),
        })

    results.sort(key=lambda r: r["similarity"], reverse=True)
    return results[:top_k]
