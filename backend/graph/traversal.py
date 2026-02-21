"""Handoff Backend — Graph Traversal Module.

Provides the high-level graph navigation logic used by ADK tools.
"""

from __future__ import annotations

import re
import yaml

from core.storage import read_node, read_static_node, list_client_nodes
from graph.search import search_nodes


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown."""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        metadata = {}
    return metadata, parts[2].strip()


def _extract_links(content: str) -> list[str]:
    """Extract all [[wikilink]] references from content."""
    return re.findall(r'\[\[([^\]]+)\]\]', content)


def get_index(client_id: str, layer: str = "client") -> dict:
    """Read the index/MOC node for a given layer.

    Args:
        client_id: Client identifier.
        layer: "client", "product", or "industry"

    Returns:
        Dict with node content, metadata, and available links.
    """
    if layer == "product":
        content = read_static_node("product/index.md")
        node_id = "product-index"
    elif layer == "industry":
        content = read_static_node("industries/index.md")
        node_id = "industry-index"
    else:
        # Client layer — try {client-slug}-index
        nodes = list_client_nodes(client_id)
        index_nodes = [n for n in nodes if n.endswith("-index")]
        node_id = index_nodes[0] if index_nodes else nodes[0] if nodes else None
        if not node_id:
            return {"error": f"No graph found for client {client_id}", "available_nodes": []}
        content = read_node(client_id, node_id)

    if not content:
        return {"error": f"Index node not found for {layer} layer", "available_nodes": []}

    metadata, body = _parse_frontmatter(content)
    links = _extract_links(content)

    return {
        "node_id": node_id,
        "title": metadata.get("title", node_id),
        "content": body,
        "links": links,
        "metadata": metadata,
    }


def follow_link(client_id: str, node_id: str, sections_only: bool = False) -> dict:
    """Follow a wikilink to read a specific node.

    Searches client nodes first, then static product/industry nodes.

    Args:
        client_id: Client identifier.
        node_id: The node_id to navigate to.
        sections_only: If True, returns only H2 headers for progressive disclosure.

    Returns:
        Dict with node content, metadata, and outgoing links.
    """
    # Try client node first
    content = read_node(client_id, node_id)

    # Try static product node
    if not content:
        content = read_static_node(f"product/{node_id}.md")

    # Try static industry nodes (check manufacturing subdirectory)
    if not content:
        content = read_static_node(f"industries/manufacturing/{node_id.replace('manufacturing-', '')}.md")

    # Try industry index
    if not content:
        content = read_static_node(f"industries/{node_id}.md")

    if not content:
        return {
            "error": f"Node '{node_id}' not found in any layer",
            "suggestion": "Use search_graph to find relevant nodes",
        }

    metadata, body = _parse_frontmatter(content)
    links = _extract_links(content)

    if sections_only:
        # Filter body to only include headers (specifically H2 logic as per PRD)
        lines = body.split("\n")
        headers = [line for line in lines if line.startswith("#")]
        if headers:
            body = "\n".join(headers)
        else:
            body = "(Node has no section headers)"

    return {
        "node_id": node_id,
        "title": metadata.get("title", node_id),
        "layer": metadata.get("layer", "unknown"),
        "content": body,
        "links": links,
        "description": metadata.get("description", ""),
    }


def search_graph(client_id: str, query: str) -> dict:
    """Semantic search across the client's skill graph.

    Uses gemini-embedding-001 to find the most relevant nodes.

    Args:
        client_id: Client identifier.
        query: Natural language search query.

    Returns:
        Dict with ranked search results.
    """
    results = search_nodes(client_id, query, top_k=5)

    return {
        "query": query,
        "results": results,
        "result_count": len(results),
        "suggestion": "Use follow_link(node_id) to read the full content of any result",
    }
