"""Synapse Backend — ADK Agent Tools.

Defines the three graph traversal tools that the ADK agent uses
during conversations to navigate the client skill graph.
"""

from __future__ import annotations

import json
from graph.traversal import get_index, follow_link, search_graph


def read_index(client_id: str, layer: str = "client") -> str:
    """Read the index/table-of-contents node for a skill graph layer.

    Use this tool FIRST when starting a briefing to understand what knowledge
    is available. Start with the client layer, then explore product or industry
    layers as needed.

    Args:
        client_id: The client identifier (e.g., "opp-2026-gm001")
        layer: Which layer to read. Options: "client", "product", "industry"

    Returns:
        The index node content with available links to follow.
    """
    result = get_index(client_id, layer)
    return json.dumps(result, indent=2, default=str)


def tool_follow_link(client_id: str, node_id: str, sections_only: bool = False) -> str:
    """Navigate to a specific node in the skill graph by following a wikilink.

    Use this tool when a [[wikilink]] in the current node is relevant to
    the CSM's question. The tool resolves links across all layers:
    client nodes, product nodes, and industry nodes.
    Set sections_only=True to read just the headers first if the node is long.

    Args:
        client_id: The client identifier
        node_id: The node_id to navigate to (from a [[wikilink]] reference)
        sections_only: If True, returns only the section headers

    Returns:
        The node content with its metadata and outgoing links.
    """
    result = follow_link(client_id, node_id, sections_only)
    return json.dumps(result, indent=2, default=str)


def tool_search_graph(client_id: str, query: str) -> str:
    """Search across the client's entire skill graph using semantic search.

    Use this tool when the CSM asks a question and you don't know which
    specific node contains the answer. The search uses vector embeddings
    to find the most relevant nodes.

    Args:
        client_id: The client identifier
        query: Natural language search query describing what you're looking for

    Returns:
        Ranked list of relevant nodes with similarity scores.
        Use follow_link() to read the full content of promising results.
    """
    result = search_graph(client_id, query)
    return json.dumps(result, indent=2, default=str)


# Tool definitions for ADK / Gemini function calling
TOOL_DEFINITIONS = [
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
                "sections_only": {"type": "boolean", "description": "If true, returns only the section headers to save context window"},
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
    "read_index": read_index,
    "follow_link": tool_follow_link,
    "search_graph": tool_search_graph,
}
