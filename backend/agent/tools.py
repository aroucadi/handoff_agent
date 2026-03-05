"""Synapse Backend — ADK Agent Tools.

Defines graph traversal and knowledge retrieval tools for the ADK agent.
Supports both structured entity+edge graphs (Phase 2) and legacy markdown graphs.
"""

from __future__ import annotations

import json
from graph.traversal import (
    # Legacy
    get_index, follow_link, search_graph,
    # Structured
    get_entity, get_entities_by_type, traverse_from,
    get_graph_overview, get_risk_profile, get_product_knowledge,
)
from graph.search import search_entities


# ── Tool Functions ────────────────────────────────────────────────

def tool_graph_overview(client_id: str) -> str:
    """Get a high-level overview of the client's knowledge graph.

    Use this tool FIRST when starting a briefing to understand what knowledge
    is available, how many entities and edges exist, and which format the
    graph uses (structured or markdown).

    Args:
        client_id: The client identifier (e.g., "demo_tenant_acme-corp")

    Returns:
        Graph statistics, entity type breakdown, and key entities.
    """
    result = get_graph_overview(client_id)
    return json.dumps(result, indent=2, default=str)


def tool_get_entity(client_id: str, entity_id: str) -> str:
    """Retrieve a specific entity and its connections from the knowledge graph.

    Use this when you know the entity_id (from search or traversal results)
    and need full details including all connected edges.

    Args:
        client_id: The client identifier
        entity_id: The entity ID to retrieve (e.g., "demo_tenant_acme-corp_org")

    Returns:
        Entity properties, outgoing edges, and incoming edges.
    """
    result = get_entity(client_id, entity_id)
    return json.dumps(result, indent=2, default=str)


def tool_get_entities_by_type(client_id: str, entity_type: str) -> str:
    """Get all entities of a specific type for a client.

    Use this to get all risks, contacts, products, or any other entity type.
    Valid types: Organization, Deal, Contact, Activity, Contract, Renewal,
    Product, Feature, UseCase, KBArticle, Limitation, Integration,
    Risk, DeriskingStrategy, SuccessMetric, Milestone, Objection,
    Commitment, CompetitorMention.

    Args:
        client_id: The client identifier
        entity_type: The entity type name (e.g., "Risk", "Contact", "Product")

    Returns:
        List of entities matching the type with their properties.
    """
    result = get_entities_by_type(client_id, entity_type)
    return json.dumps(result, indent=2, default=str)


def tool_traverse_graph(client_id: str, entity_id: str, edge_type: str = None, max_hops: int = 1) -> str:
    """Multi-hop graph traversal starting from a given entity.

    Follows outgoing edges from the starting entity, discovering connected
    entities up to max_hops levels deep. Optionally filter by edge type.

    Example: traverse from an Organization with edge_type="HAS_DEAL" to find
    all deals, then from a Deal with "HAS_RISK" to find risks.

    Args:
        client_id: The client identifier
        entity_id: Starting entity ID
        edge_type: Optional edge type filter (e.g., "HAS_RISK", "INCLUDES", "CHAMPIONS")
        max_hops: Traversal depth, 1-3 (default: 1)

    Returns:
        Discovered entities and edges in the subgraph.
    """
    result = traverse_from(client_id, entity_id, edge_type, max_hops)
    return json.dumps(result, indent=2, default=str)


def tool_search_entities(client_id: str, query: str, entity_type: str = None) -> str:
    """Semantic search across the client's knowledge graph entities.

    Use this when you need to find entities related to a topic but don't
    know their IDs. Optionally filter by entity type for targeted results.

    Args:
        client_id: The client identifier
        query: Natural language search query
        entity_type: Optional entity type filter (e.g., "Risk", "Feature")

    Returns:
        Ranked list of relevant entities with properties.
    """
    results = search_entities(client_id, query, entity_type)
    return json.dumps({
        "query": query,
        "entity_type_filter": entity_type,
        "results": results,
        "result_count": len(results),
        "suggestion": "Use get_entity(entity_id) for full details including connections",
    }, indent=2, default=str)


def tool_risk_profile(client_id: str) -> str:
    """Get a comprehensive risk profile for a client's deal.

    Returns all identified risks with severity breakdown and associated
    derisking strategies. Use this for risk-focused briefing sections.

    Args:
        client_id: The client identifier

    Returns:
        All risks, severity breakdown, and available derisking strategies.
    """
    result = get_risk_profile(client_id)
    return json.dumps(result, indent=2, default=str)


def tool_product_knowledge(client_id: str) -> str:
    """Get product knowledge relevant to a client's deal.

    Returns all products in the deal with their features, known limitations,
    and related KB articles. Use this for product-focused discussion or
    to answer questions about capabilities and constraints.

    Args:
        client_id: The client identifier

    Returns:
        Products with features, limitations, and documentation links.
    """
    result = get_product_knowledge(client_id)
    return json.dumps(result, indent=2, default=str)


# ── Legacy Tools (kept for backward compat) ──────────────────────

def read_index(client_id: str, layer: str = "client") -> str:
    """Read the index/table-of-contents node for a skill graph layer (legacy markdown mode).

    Args:
        client_id: The client identifier
        layer: Which layer to read. Options: "client", "product", "industry"

    Returns:
        The index node content with available links to follow.
    """
    result = get_index(client_id, layer)
    return json.dumps(result, indent=2, default=str)


def tool_follow_link(client_id: str, node_id: str, sections_only: bool = False) -> str:
    """Navigate to a specific node by following a wikilink (legacy markdown mode).

    Args:
        client_id: The client identifier
        node_id: The node_id to navigate to
        sections_only: If True, returns only the section headers

    Returns:
        The node content with metadata and outgoing links.
    """
    result = follow_link(client_id, node_id, sections_only)
    return json.dumps(result, indent=2, default=str)


def tool_search_graph(client_id: str, query: str) -> str:
    """Semantic search across the client's skill graph (legacy markdown mode).

    Args:
        client_id: The client identifier
        query: Natural language search query

    Returns:
        Ranked list of relevant nodes.
    """
    result = search_graph(client_id, query)
    return json.dumps(result, indent=2, default=str)


# ── Tool Definitions for ADK / Gemini Function Calling ────────────

TOOL_DEFINITIONS = [
    # ── Structured Graph Tools (Primary) ──
    {
        "name": "graph_overview",
        "description": tool_graph_overview.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "The client identifier"},
            },
            "required": ["client_id"],
        },
    },
    {
        "name": "get_entity",
        "description": tool_get_entity.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "The client identifier"},
                "entity_id": {"type": "string", "description": "Entity ID to retrieve"},
            },
            "required": ["client_id", "entity_id"],
        },
    },
    {
        "name": "get_entities_by_type",
        "description": tool_get_entities_by_type.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "The client identifier"},
                "entity_type": {
                    "type": "string",
                    "description": "Entity type name (e.g., Risk, Contact, Product, Feature)",
                },
            },
            "required": ["client_id", "entity_type"],
        },
    },
    {
        "name": "traverse_graph",
        "description": tool_traverse_graph.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "The client identifier"},
                "entity_id": {"type": "string", "description": "Starting entity ID"},
                "edge_type": {"type": "string", "description": "Optional edge type filter (e.g., HAS_RISK, INCLUDES)"},
                "max_hops": {"type": "integer", "description": "Traversal depth 1-3 (default: 1)"},
            },
            "required": ["client_id", "entity_id"],
        },
    },
    {
        "name": "search_entities",
        "description": tool_search_entities.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "The client identifier"},
                "query": {"type": "string", "description": "Natural language search query"},
                "entity_type": {"type": "string", "description": "Optional type filter (e.g., Risk, Feature)"},
            },
            "required": ["client_id", "query"],
        },
    },
    {
        "name": "risk_profile",
        "description": tool_risk_profile.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "The client identifier"},
            },
            "required": ["client_id"],
        },
    },
    {
        "name": "product_knowledge",
        "description": tool_product_knowledge.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "The client identifier"},
            },
            "required": ["client_id"],
        },
    },
    # ── Legacy Tools ──
    {
        "name": "read_index",
        "description": read_index.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "The client identifier"},
                "layer": {
                    "type": "string",
                    "enum": ["client", "product", "industry"],
                    "description": "Which knowledge layer to read the index for",
                },
            },
            "required": ["client_id"],
        },
    },
    {
        "name": "follow_link",
        "description": tool_follow_link.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "The client identifier"},
                "node_id": {"type": "string", "description": "The node_id to navigate to"},
                "sections_only": {"type": "boolean", "description": "If true, returns only section headers"},
            },
            "required": ["client_id", "node_id"],
        },
    },
    {
        "name": "search_graph",
        "description": tool_search_graph.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "The client identifier"},
                "query": {"type": "string", "description": "Natural language search query"},
            },
            "required": ["client_id", "query"],
        },
    },
]


# Map tool names to functions for execution
TOOL_FUNCTIONS = {
    # Structured
    "graph_overview": tool_graph_overview,
    "get_entity": tool_get_entity,
    "get_entities_by_type": tool_get_entities_by_type,
    "traverse_graph": tool_traverse_graph,
    "search_entities": tool_search_entities,
    "risk_profile": tool_risk_profile,
    "product_knowledge": tool_product_knowledge,
    # Legacy
    "read_index": read_index,
    "follow_link": tool_follow_link,
    "search_graph": tool_search_graph,
}
