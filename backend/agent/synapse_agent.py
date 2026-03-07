"""Synapse Backend — Agent Definition.

Defines the Synapse CSM briefing agent using Gemini with function calling.
This agent navigates the skill graph to provide grounded answers.
"""

from __future__ import annotations

import json
import asyncio
from datetime import datetime

from google import genai
from google.genai.types import (
    Content,
    FunctionDeclaration,
    GenerateContentConfig,
    Part,
    Tool,
)

from config import config
from agent.prompts import SYNAPSE_SYSTEM_PROMPT
from agent.tools import TOOL_FUNCTIONS


def _build_tools() -> list[Tool]:
    """Build Gemini function-calling tool definitions."""
    declarations = [
        FunctionDeclaration(
            name="read_index",
            description="Read the index/table-of-contents node for a skill graph layer. "
                        "Use FIRST when starting a briefing to understand available knowledge.",
            parameters={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "The account identifier"},
                    "layer": {
                        "type": "string",
                        "enum": ["account", "product", "industry"],
                        "description": "Which knowledge layer to read",
                    },
                },
                "required": ["account_id"],
            },
        ),
        FunctionDeclaration(
            name="follow_link",
            description="Navigate to a specific node in the skill graph. "
                        "Use when a [[wikilink]] in the current node is relevant. "
                        "Set sections_only to true to preview long nodes first.",
            parameters={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "The account identifier"},
                    "node_id": {"type": "string", "description": "The node_id to navigate to"},
                    "sections_only": {"type": "boolean", "description": "Return only headers"},
                },
                "required": ["account_id", "node_id"],
            },
        ),
        FunctionDeclaration(
            name="search_graph",
            description="Semantic search across the client's skill graph. "
                        "Use when you don't know which node has the answer.",
            parameters={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "The account identifier"},
                    "query": {"type": "string", "description": "Natural language search query"},
                },
                "required": ["account_id", "query"],
            },
        ),
    ]

    return [Tool(function_declarations=declarations)]


async def run_text_conversation(
    account_id: str,
    message: str,
    history: list[dict] | None = None,
    brand_name: str = "ClawdView",
) -> dict:
    """Run a single turn of text conversation with the Synapse agent.
    
    brand_name: Custom platform name from tenant config.
    """
    client = genai.Client(vertexai=True, project=config.project_id, location=config.gen_region)
    tools = _build_tools()

    # Build conversation history
    contents: list[Content] = []
    if history:
        for turn in history:
            role = turn.get("role", "user")
            text = turn.get("text", "")
            contents.append(Content(role=role, parts=[Part.from_text(text=text)]))

    # Add current user message
    contents.append(Content(role="user", parts=[Part.from_text(text=message)]))

    # Format system instruction with brand name
    system_instruction = SYNAPSE_SYSTEM_PROMPT.replace("{brand_name}", brand_name).replace("ClawdView", brand_name)

    gen_config = GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3,
        max_output_tokens=4096,
        tools=tools,
    )

    tool_calls_log = []
    nodes_visited = []

    # Wrapper functions to hide account_id from the model and log calls
    def get_index(layer: str = "account") -> str:
        """Read the index/table-of-contents node for a skill graph layer. Use this FIRST when starting a briefing."""
        tool_calls_log.append({"tool": "read_index", "args": {"layer": layer}})
        return TOOL_FUNCTIONS["read_index"](account_id, layer)

    def follow_link(node_id: str, sections_only: bool = False) -> str:
        """Navigate to a specific node in the skill graph by following a wikilink."""
        tool_calls_log.append({"tool": "follow_link", "args": {"node_id": node_id, "sections_only": sections_only}})
        nodes_visited.append(node_id)
        return TOOL_FUNCTIONS["follow_link"](account_id, node_id, sections_only)

    def search_graph(query: str) -> str:
        """Search across the account's entire skill graph using semantic search."""
        tool_calls_log.append({"tool": "search_graph", "args": {"query": query}})
        return TOOL_FUNCTIONS["search_graph"](account_id, query)

    from google.genai.types import AutomaticFunctionCallingConfig
    
    gen_config = GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3,
        tools=[get_index, follow_link, search_graph],
        automatic_function_calling=AutomaticFunctionCallingConfig(disable=False),
    )

    chat = client.aio.chats.create(
        model=config.graph_gen_model,
        config=gen_config,
        history=contents,
    )

    start_time = datetime.utcnow()
    try:
        response = await chat.send_message(message)
        agent_response = response.text
        
        # Extract usage
        prompt_tokens = 0
        completion_tokens = 0
        if getattr(response, "usage_metadata", None):
            prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
            completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)
            
        from core.telemetry import record_trace
        asyncio.create_task(
            record_trace(
                agent_name="synapse_text_agent",
                job_id="chat-turn",
                start_time=start_time,
                end_time=datetime.utcnow(),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                tools_used=tool_calls_log,
                client_id=account_id,
            )
        )
        
    except Exception as e:
        agent_response = f"Sorry, I encountered an error coordinating tool execution: {e}"

    return {
        "response": agent_response,
        "tool_calls": tool_calls_log,
        "nodes_visited": nodes_visited,
        "rounds": len(tool_calls_log) + 1,
    }
