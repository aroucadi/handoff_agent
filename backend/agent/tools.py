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

def tool_graph_overview(tenant_id: str, account_id: str, **kwargs) -> str:
    """Get a high-level overview of the account's knowledge graph.

    Args:
        tenant_id: The tenant identifier
        account_id: The account identifier (e.g., "demo_tenant_acme-corp")

    Returns:
        Graph statistics, entity type breakdown, and key entities.
    """
    result = get_graph_overview(tenant_id, account_id)
    return json.dumps(result, indent=2, default=str)


def tool_get_entity(tenant_id: str, account_id: str, entity_id: str, **kwargs) -> str:
    """Retrieve a specific entity and its connections from the knowledge graph.

    Args:
        tenant_id: The tenant identifier
        account_id: The account identifier
        entity_id: The entity ID to retrieve

    Returns:
        Entity properties, outgoing edges, and incoming edges.
    """
    result = get_entity(tenant_id, account_id, entity_id)
    return json.dumps(result, indent=2, default=str)


def tool_get_entities_by_type(tenant_id: str, account_id: str, entity_type: str, **kwargs) -> str:
    """Get all entities of a specific type for an account.

    Args:
        tenant_id: The tenant identifier
        account_id: The account identifier
        entity_type: The entity type name (e.g., "Risk", "Contact", "Product")

    Returns:
        List of entities matching the type with their properties.
    """
    result = get_entities_by_type(tenant_id, account_id, entity_type)
    return json.dumps(result, indent=2, default=str)


def tool_traverse_graph(tenant_id: str, account_id: str, entity_id: str, edge_type: str = None, max_hops: int = 1, **kwargs) -> str:
    """Multi-hop graph traversal starting from a given entity.

    Args:
        tenant_id: The tenant identifier
        account_id: The account identifier
        entity_id: Starting entity ID
        edge_type: Optional edge type filter
        max_hops: Traversal depth, 1-3 (default: 1)

    Returns:
        Discovered entities and edges in the subgraph.
    """
    result = traverse_from(tenant_id, account_id, entity_id, edge_type, max_hops)
    return json.dumps(result, indent=2, default=str)


def tool_search_entities(tenant_id: str, account_id: str, query: str, entity_type: str = None, **kwargs) -> str:
    """Semantic search across the account's knowledge graph entities.

    Args:
        tenant_id: The tenant identifier
        account_id: The account identifier
        query: Natural language search query
        entity_type: Optional entity type filter

    Returns:
        Ranked list of relevant entities with properties.
    """
    # Note: search_entities in graph/search.py might need tenant_id too if it has a shared index
    results = search_entities(tenant_id, account_id, query, entity_type)
    return json.dumps({
        "query": query,
        "entity_type_filter": entity_type,
        "results": results,
        "result_count": len(results),
        "suggestion": "Use get_entity(entity_id) for full details including connections",
    }, indent=2, default=str)


def tool_risk_profile(tenant_id: str, account_id: str, **kwargs) -> str:
    """Get a comprehensive risk profile for an account's case.

    Args:
        tenant_id: The tenant identifier
        account_id: The account identifier

    Returns:
        All risks, severity breakdown, and available derisking strategies.
    """
    result = get_risk_profile(tenant_id, account_id)
    return json.dumps(result, indent=2, default=str)


def tool_product_knowledge(tenant_id: str, account_id: str, **kwargs) -> str:
    """Get product knowledge relevant to an account's case.

    Args:
        tenant_id: The tenant identifier
        account_id: The account identifier

    Returns:
        Products with features, limitations, and documentation links.
    """
    result = get_product_knowledge(tenant_id, account_id)
    return json.dumps(result, indent=2, default=str)


# ── Legacy Tools (kept for backward compat) ──────────────────────

def read_index(tenant_id: str, account_id: str, layer: str = "account", **kwargs) -> str:
    """Read the index/table-of-contents node for a skill graph layer (legacy markdown mode).

    Args:
        tenant_id: The tenant identifier
        account_id: The account identifier
        layer: Which layer to read. Options: "account", "product", "industry"

    Returns:
        The index node content with available links to follow.
    """
    result = get_index(tenant_id, account_id, layer)
    return json.dumps(result, indent=2, default=str)


def tool_follow_link(tenant_id: str, account_id: str, node_id: str, sections_only: bool = False, **kwargs) -> str:
    """Navigate to a specific node by following a wikilink (legacy markdown mode).

    Args:
        tenant_id: The tenant identifier
        account_id: The account identifier
        node_id: The node_id to navigate to
        sections_only: If True, returns only the section headers

    Returns:
        The node content with metadata and outgoing links.
    """
    result = follow_link(tenant_id, account_id, node_id, sections_only)
    return json.dumps(result, indent=2, default=str)


def tool_search_graph(tenant_id: str, account_id: str, query: str, **kwargs) -> str:
    """Semantic search across the account's skill graph (legacy markdown mode).

    Args:
        tenant_id: The tenant identifier
        account_id: The account identifier
        query: Natural language search query

    Returns:
        Ranked list of relevant nodes.
    """
    result = search_graph(tenant_id, account_id, query)
    return json.dumps(result, indent=2, default=str)


# ── Output Generation Tools ──────────────────────────────────────

async def tool_generate_briefing(tenant_id: str, account_id: str, csm_name: str = "CSM", **kwargs) -> str:
    """Generate a pre-meeting briefing summary from the knowledge graph.

    Args:
        tenant_id: The tenant identifier
        account_id: The client/account identifier
        csm_name: CSM name for personalization (optional)

    Returns:
        Generated briefing document in Markdown format.
    """
    from graph.outputs import generate_briefing
    result = await generate_briefing(tenant_id, account_id, csm_name)
    return json.dumps({"title": result["title"], "content": result["content"][:3000]}, indent=2, default=str)


async def tool_generate_action_plan(tenant_id: str, account_id: str, meeting_notes: str = None, **kwargs) -> str:
    """Generate a post-session action plan based on graph data.

    Args:
        tenant_id: The tenant identifier
        account_id: The client/account identifier
        meeting_notes: Optional notes or context from the session

    Returns:
        Generated action plan document in Markdown format.
    """
    from graph.outputs import generate_action_plan
    result = await generate_action_plan(tenant_id, account_id, meeting_notes)
    return json.dumps({"title": result["title"], "content": result["content"][:3000]}, indent=2, default=str)


async def tool_generate_transcript(
    tenant_id: str,
    account_id: str,
    transcript_type: str = "sales_script",
    user_role: str = None,
    additional_context: str = None,
    **kwargs
) -> str:
    """Generate a role-based transcript or conversation script from the knowledge graph.

    Args:
        tenant_id: The tenant identifier
        account_id: The client/account identifier
        transcript_type: One of the supported transcript types
        user_role: Optional role (e.g., "AE", "CSM")
        additional_context: Optional extra context or session notes

    Returns:
        Generated transcript/script document in Markdown format.
    """
    from graph.outputs import generate_transcript
    result = await generate_transcript(tenant_id, account_id, transcript_type, user_role, additional_context)
    if "error" in result:
        return json.dumps(result, indent=2)
    return json.dumps({"title": result["title"], "content": result["content"][:3000]}, indent=2, default=str)


async def tool_web_scrape(url: str, **kwargs) -> str:
    """Fetch and scrape the text content of a public website URL.
    
    Use this for real-time browsing when the knowledge graph doesn't have 
    latest company info or the specific page details.
    
    Args:
        url: The full URL to scrape
        
    Returns:
        Structured text content of the page.
    """
    import httpx
    from bs4 import BeautifulSoup
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {"User-Agent": "SynapseAgent/1.0 (Mozilla/5.0)"}
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Remove noise
            for s in soup(["script", "style", "nav", "footer", "header"]):
                s.decompose()
                
            text = soup.get_text(separator="\n", strip=True)
            # Limit length to avoid context overflow
            return json.dumps({
                "url": url,
                "content": text[:8000],
                "status": "success"
            }, indent=2)
    except Exception as e:
        return json.dumps({"url": url, "error": str(e), "status": "failed"}, indent=2)


# ── Tool Definitions for ADK / Gemini Function Calling ────────────


TOOL_DEFINITIONS = [
    # ── Structured Graph Tools (Primary) ──
    {
        "name": "graph_overview",
        "description": tool_graph_overview.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
            },
            "required": ["tenant_id", "account_id"],
        },
    },
    {
        "name": "get_entity",
        "description": tool_get_entity.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
                "entity_id": {"type": "string", "description": "Entity ID to retrieve"},
            },
            "required": ["tenant_id", "account_id", "entity_id"],
        },
    },
    {
        "name": "get_entities_by_type",
        "description": tool_get_entities_by_type.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
                "entity_type": {
                    "type": "string",
                    "description": "Entity type name (e.g. Risk, Contact, Product, Feature)",
                },
            },
            "required": ["tenant_id", "account_id", "entity_type"],
        },
    },
    {
        "name": "traverse_graph",
        "description": tool_traverse_graph.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
                "entity_id": {"type": "string", "description": "Starting entity ID"},
                "edge_type": {"type": "string", "description": "Optional edge type filter (e.g. HAS_RISK, INCLUDES)"},
                "max_hops": {"type": "integer", "description": "Traversal depth 1-3 (default: 1)"},
            },
            "required": ["tenant_id", "account_id", "entity_id"],
        },
    },
    {
        "name": "search_entities",
        "description": tool_search_entities.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
                "query": {"type": "string", "description": "Natural language search query"},
                "entity_type": {"type": "string", "description": "Optional type filter (e.g. Risk, Feature)"},
            },
            "required": ["tenant_id", "account_id", "query"],
        },
    },
    {
        "name": "risk_profile",
        "description": tool_risk_profile.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
            },
            "required": ["tenant_id", "account_id"],
        },
    },
    {
        "name": "product_knowledge",
        "description": tool_product_knowledge.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
            },
            "required": ["tenant_id", "account_id"],
        },
    },
    # ── Legacy Tools ──
    {
        "name": "read_index",
        "description": read_index.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
                "layer": {
                    "type": "string",
                    "enum": ["account", "product", "industry"],
                    "description": "Which knowledge layer to read the index for",
                },
            },
            "required": ["tenant_id", "account_id"],
        },
    },
    {
        "name": "follow_link",
        "description": tool_follow_link.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
                "node_id": {"type": "string", "description": "The node_id to navigate to"},
                "sections_only": {"type": "boolean", "description": "If true, returns only section headers"},
            },
            "required": ["tenant_id", "account_id", "node_id"],
        },
    },
    {
        "name": "search_graph",
        "description": tool_search_graph.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
                "query": {"type": "string", "description": "Natural language search query"},
            },
            "required": ["tenant_id", "account_id", "query"],
        },
    },
    # ── Output Generation Tools ──
    {
        "name": "generate_briefing",
        "description": tool_generate_briefing.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
                "csm_name": {"type": "string", "description": "CSM name for personalization"},
            },
            "required": ["tenant_id", "account_id"],
        },
    },
    {
        "name": "generate_action_plan",
        "description": tool_generate_action_plan.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
                "meeting_notes": {"type": "string", "description": "Optional notes from the session"},
            },
            "required": ["tenant_id", "account_id"],
        },
    },
    {
        "name": "generate_transcript",
        "description": tool_generate_transcript.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "The tenant identifier"},
                "account_id": {"type": "string", "description": "The account identifier"},
                "transcript_type": {
                    "type": "string",
                    "description": "One of: sales_script, support_script, qbr_prep, renewal_script, onboarding_guide, discovery_questions",
                },
                "user_role": {"type": "string", "description": "Optional role (e.g., AE, CSM)"},
                "additional_context": {"type": "string", "description": "Optional extra context"},
            },
            "required": ["tenant_id", "account_id", "transcript_type"],
        },
    },
    {
        "name": "web_scrape",
        "description": tool_web_scrape.__doc__,
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The full URL to browse and scrape"},
            },
            "required": ["url"],
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
    # Outputs
    "generate_briefing": tool_generate_briefing,
    "generate_action_plan": tool_generate_action_plan,
    "generate_transcript": tool_generate_transcript,
    "web_scrape": tool_web_scrape,
}

