"""Synapse Backend — Graph Traversal Module.

Provides graph navigation logic used by ADK tools.
Supports both:
  - Structured entity+edge graphs (Phase 1B) stored in `knowledge_graphs/`
  - Legacy markdown wikilink graphs stored in GCS via `skill_graphs/`
"""

from __future__ import annotations

import re
import yaml

from core.auth import verify_tenant_access

from fastapi import HTTPException

def _verify_tenant_access(tenant_id: str, client_id: str):
    """Bridge to core.auth verification with FastAPI exception handling."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context required")
    
    if not verify_tenant_access(tenant_id, client_id):
        raise HTTPException(
            status_code=403, 
            detail=f"Access denied: No authoritative ownership found for {client_id} under tenant {tenant_id}"
        )


# ── Legacy Markdown Graph Traversal ──────────────────────────────

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


def get_index(tenant_id: str, client_id: str, layer: str = "client") -> dict:
    """Read the index/MOC node for a given layer (legacy markdown mode)."""
    _verify_tenant_access(tenant_id, client_id)
    if layer == "product":
        content = read_static_node("product/index.md")
        node_id = "product-index"
    elif layer == "industry":
        content = read_static_node("industries/index.md")
        node_id = "industry-index"
    else:
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


def follow_link(tenant_id: str, client_id: str, node_id: str, sections_only: bool = False) -> dict:
    """Follow a wikilink to read a specific node (legacy markdown mode)."""
    _verify_tenant_access(tenant_id, client_id)
    content = read_node(client_id, node_id)
    if not content:
        content = read_static_node(f"product/{node_id}.md")
    if not content:
        content = read_static_node(f"industries/manufacturing/{node_id.replace('manufacturing-', '')}.md")
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
        lines = body.split("\n")
        headers = [line for line in lines if line.startswith("#")]
        body = "\n".join(headers) if headers else "(Node has no section headers)"

    return {
        "node_id": node_id,
        "title": metadata.get("title", node_id),
        "layer": metadata.get("layer", "unknown"),
        "content": body,
        "links": links,
        "description": metadata.get("description", ""),
    }


def search_graph(tenant_id: str, client_id: str, query: str) -> dict:
    """Semantic search across the client's skill graph (legacy)."""
    _verify_tenant_access(tenant_id, client_id)
    results = search_nodes(tenant_id, client_id, query, top_k=5)
    return {
        "query": query,
        "results": results,
        "result_count": len(results),
        "suggestion": "Use follow_link(node_id) to read the full content of any result",
    }


# ── Structured Entity+Edge Graph Traversal (Phase 2) ─────────────

def get_entity(tenant_id: str, client_id: str, entity_id: str) -> dict:
    """Retrieve a specific entity from the structured knowledge graph.

    Args:
        tenant_id: Tenant identifier (for scoping).
        client_id: Client identifier.
        entity_id: Entity ID to retrieve.

    Returns:
        Entity dict with type, properties, and connected edges.
    """
    _verify_tenant_access(tenant_id, client_id)
    db = get_firestore_client()

    # Get the entity
    entity_ref = (db.collection("knowledge_graphs")
                  .document(client_id)
                  .collection("entities")
                  .document(entity_id))
    entity_doc = entity_ref.get()

    if not entity_doc.exists:
        return {"error": f"Entity '{entity_id}' not found", "suggestion": "Use search_entities to find entities"}

    entity_data = entity_doc.to_dict()
    # Remove embedding from response to save context window
    entity_data.pop("embedding", None)

    # Get connected edges
    edges_ref = db.collection("knowledge_graphs").document(client_id).collection("edges")

    outgoing = []
    incoming = []

    # Get edges where this entity is the source
    for doc in edges_ref.where("from_id", "==", entity_id).stream():
        edge = doc.to_dict()
        edge.pop("indexed_at", None)
        outgoing.append(edge)

    # Get edges where this entity is the target
    for doc in edges_ref.where("to_id", "==", entity_id).stream():
        edge = doc.to_dict()
        edge.pop("indexed_at", None)
        incoming.append(edge)

    return {
        "entity": entity_data,
        "outgoing_edges": outgoing,
        "incoming_edges": incoming,
        "total_connections": len(outgoing) + len(incoming),
    }


def get_entities_by_type(tenant_id: str, client_id: str, entity_type: str) -> dict:
    """Retrieve all entities of a specific type for a client.

    Args:
        tenant_id: Tenant identifier (for scoping).
        client_id: Client identifier.
        entity_type: Node type name (e.g. "Risk", "Contact", "Product").

    Returns:
        Dict with list of matching entities.
    """
    _verify_tenant_access(tenant_id, client_id)
    db = get_firestore_client()
    entities_ref = (db.collection("knowledge_graphs")
                    .document(client_id)
                    .collection("entities"))

    results = []
    for doc in entities_ref.where("type", "==", entity_type).stream():
        data = doc.to_dict()
        data.pop("embedding", None)
        results.append(data)

    return {
        "entity_type": entity_type,
        "entities": results,
        "count": len(results),
    }


def traverse_from(tenant_id: str, client_id: str, entity_id: str, edge_type: str = None, max_hops: int = 1) -> dict:
    """Multi-hop graph traversal starting from a given entity.

    Follows outgoing edges (optionally filtered by edge_type) up to max_hops
    levels deep. Returns the subgraph of discovered entities and edges.

    Args:
        tenant_id: Tenant identifier (for scoping).
        client_id: Client identifier.
        entity_id: Starting entity ID.
        edge_type: Optional edge type filter (e.g. "HAS_RISK", "INCLUDES").
        max_hops: Maximum traversal depth (1-3).

    Returns:
        Dict with discovered entities, edges, and traversal path.
    """
    _verify_tenant_access(tenant_id, client_id)
    db = get_firestore_client()
    max_hops = min(max_hops, 3)  # Cap at 3 to prevent excessive traversal

    visited_entities = set()
    discovered_entities = []
    discovered_edges = []
    frontier = [entity_id]

    entities_ref = db.collection("knowledge_graphs").document(client_id).collection("entities")
    edges_ref = db.collection("knowledge_graphs").document(client_id).collection("edges")

    for hop in range(max_hops):
        next_frontier = []

        for current_id in frontier:
            if current_id in visited_entities:
                continue
            visited_entities.add(current_id)

            # Get entity
            entity_doc = entities_ref.document(current_id).get()
            if entity_doc.exists:
                data = entity_doc.to_dict()
                data.pop("embedding", None)
                data["_hop"] = hop
                discovered_entities.append(data)

            # Get outgoing edges
            query = edges_ref.where("from_id", "==", current_id)
            if edge_type:
                query = query.where("type", "==", edge_type)

            for edge_doc in query.stream():
                edge = edge_doc.to_dict()
                edge.pop("indexed_at", None)
                discovered_edges.append(edge)
                target = edge.get("to_id", "")
                if target not in visited_entities:
                    next_frontier.append(target)

        frontier = next_frontier

    # Get the last frontier entities (leaf nodes)
    for leaf_id in frontier:
        if leaf_id not in visited_entities:
            entity_doc = entities_ref.document(leaf_id).get()
            if entity_doc.exists:
                data = entity_doc.to_dict()
                data.pop("embedding", None)
                data["_hop"] = max_hops
                discovered_entities.append(data)
                visited_entities.add(leaf_id)

    return {
        "start_entity": entity_id,
        "edge_filter": edge_type,
        "max_hops": max_hops,
        "entities": discovered_entities,
        "edges": discovered_edges,
        "entity_count": len(discovered_entities),
        "edge_count": len(discovered_edges),
    }


def get_graph_overview(tenant_id: str, client_id: str) -> dict:
    """Get a high-level overview of a client's structured knowledge graph.

    Returns entity type counts, edge type counts, and key entities
    (Organization, Deal) for orientation.

    Args:
        tenant_id: Tenant identifier (for scoping).
        client_id: Client identifier.

    Returns:
        Dict with graph statistics and key entities.
    """
    _verify_tenant_access(tenant_id, client_id)
    db = get_firestore_client()

    # Check structured graph status
    status_doc = db.collection("knowledge_graphs").document(client_id).get()
    if not status_doc.exists:
        # Fall back to legacy check
        status_doc = db.collection("skill_graphs").document(client_id).get()
        if not status_doc.exists:
            return {"error": f"No graph found for client {client_id}"}
        status = status_doc.to_dict()
        return {
            "client_id": client_id,
            "graph_format": "markdown",
            "status": status.get("status"),
            "node_count": status.get("node_count", 0),
            "node_ids": status.get("node_ids", []),
            "suggestion": "Use read_index and follow_link for markdown graphs",
        }

    status = status_doc.to_dict()

    # Get entity type breakdown
    entities_ref = db.collection("knowledge_graphs").document(client_id).collection("entities")
    type_counts = {}
    key_entities = []

    for doc in entities_ref.stream():
        data = doc.to_dict()
        entity_type = data.get("type", "Unknown")
        type_counts[entity_type] = type_counts.get(entity_type, 0) + 1

        # Collect key entities for quick reference
        if entity_type in ("Organization", "Deal"):
            key_entities.append({
                "id": data.get("entity_id"),
                "type": entity_type,
                "name": data.get("properties", {}).get("name", ""),
            })

    return {
        "client_id": client_id,
        "graph_format": status.get("graph_format", "structured"),
        "status": status.get("status"),
        "entity_count": status.get("entity_count", 0),
        "edge_count": status.get("edge_count", 0),
        "entity_types": type_counts,
        "key_entities": key_entities,
        "suggestion": "Use get_entity(entity_id) or traverse_from(entity_id) to explore",
    }


def get_risk_profile(tenant_id: str, client_id: str) -> dict:
    """Get a comprehensive risk profile for a client's deal.

    Retrieves all Risk entities and their associated DeriskingStrategies,
    providing a single-tool risk assessment view.

    Args:
        tenant_id: Tenant identifier (for scoping).
        client_id: Client identifier.

    Returns:
        Dict with risks, derisking strategies, and severity breakdown.
    """
    _verify_tenant_access(tenant_id, client_id)
    db = get_firestore_client()
    entities_ref = db.collection("knowledge_graphs").document(client_id).collection("entities")
    edges_ref = db.collection("knowledge_graphs").document(client_id).collection("edges")

    risks = []
    strategies = {}
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    # Get all risks
    for doc in entities_ref.where("type", "==", "Risk").stream():
        data = doc.to_dict()
        data.pop("embedding", None)
        severity = data.get("properties", {}).get("severity", "medium").lower()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        risks.append(data)

    # Get all derisking strategies
    for doc in entities_ref.where("type", "==", "DeriskingStrategy").stream():
        data = doc.to_dict()
        data.pop("embedding", None)
        strategies[data.get("entity_id", "")] = data

    # Link strategies to risks via MITIGATED_BY edges
    risk_mitigations = {}
    for doc in edges_ref.where("type", "==", "MITIGATED_BY").stream():
        edge = doc.to_dict()
        risk_id = edge.get("from_id", "")
        strategy_id = edge.get("to_id", "")
        if strategy_id in strategies:
            risk_mitigations.setdefault(risk_id, []).append(strategies[strategy_id])

    # Enrich risks with their strategies
    for risk in risks:
        risk_id = risk.get("entity_id", "")
        risk["derisking_strategies"] = risk_mitigations.get(risk_id, [])

    return {
        "client_id": client_id,
        "risks": risks,
        "risk_count": len(risks),
        "severity_breakdown": severity_counts,
        "strategies_available": len(strategies),
    }


def get_product_knowledge(tenant_id: str, client_id: str) -> dict:
    """Get product knowledge relevant to a client's deal.

    Retrieves Products included in the deal, their Features, Limitations,
    and relevant KB articles.

    Args:
        tenant_id: Tenant identifier (for scoping).
        client_id: Client identifier.

    Returns:
        Dict with products, features, limitations, and articles.
    """
    _verify_tenant_access(tenant_id, client_id)
    db = get_firestore_client()
    entities_ref = db.collection("knowledge_graphs").document(client_id).collection("entities")
    edges_ref = db.collection("knowledge_graphs").document(client_id).collection("edges")

    products = []
    features = {}
    limitations = {}
    articles = {}

    # Get products
    for doc in entities_ref.where("type", "==", "Product").stream():
        data = doc.to_dict()
        data.pop("embedding", None)
        products.append(data)

    # Get features
    for doc in entities_ref.where("type", "==", "Feature").stream():
        data = doc.to_dict()
        data.pop("embedding", None)
        features[data.get("entity_id", "")] = data

    # Get limitations
    for doc in entities_ref.where("type", "==", "Limitation").stream():
        data = doc.to_dict()
        data.pop("embedding", None)
        limitations[data.get("entity_id", "")] = data

    # Get KB articles
    for doc in entities_ref.where("type", "==", "KBArticle").stream():
        data = doc.to_dict()
        data.pop("embedding", None)
        articles[data.get("entity_id", "")] = data

    # Link features and limitations to products via edges
    for product in products:
        pid = product.get("entity_id", "")
        product_features = []
        product_limitations = []

        for doc in edges_ref.where("from_id", "==", pid).stream():
            edge = doc.to_dict()
            if edge.get("type") == "HAS_FEATURE":
                feat = features.get(edge.get("to_id", ""))
                if feat:
                    product_features.append(feat)
            elif edge.get("type") == "DOCUMENTED_IN":
                art = articles.get(edge.get("to_id", ""))
                if art:
                    product.setdefault("articles", []).append(art)

        # Get limitations through features
        for feat in product_features:
            fid = feat.get("entity_id", "")
            for doc in edges_ref.where("from_id", "==", fid).where("type", "==", "HAS_LIMITATION").stream():
                edge = doc.to_dict()
                lim = limitations.get(edge.get("to_id", ""))
                if lim:
                    product_limitations.append(lim)

        product["features"] = product_features
        product["limitations"] = product_limitations

    return {
        "client_id": client_id,
        "products": products,
        "product_count": len(products),
        "total_features": len(features),
        "total_limitations": len(limitations),
        "total_articles": len(articles),
    }
