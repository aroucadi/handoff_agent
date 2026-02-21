"""Handoff Backend — Agent Definition.

Defines the Handoff CSM briefing agent using Gemini with function calling.
This agent navigates the skill graph to provide grounded answers.
"""

from __future__ import annotations

import json

from google import genai
from google.genai.types import (
    Content,
    FunctionDeclaration,
    GenerateContentConfig,
    Part,
    Tool,
)

from config import config
from agent.prompts import HANDOFF_SYSTEM_PROMPT
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
                    "client_id": {"type": "string", "description": "The client identifier"},
                    "layer": {
                        "type": "string",
                        "enum": ["client", "product", "industry"],
                        "description": "Which knowledge layer to read",
                    },
                },
                "required": ["client_id"],
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
                    "client_id": {"type": "string", "description": "The client identifier"},
                    "node_id": {"type": "string", "description": "The node_id to navigate to"},
                    "sections_only": {"type": "boolean", "description": "Return only headers"},
                },
                "required": ["client_id", "node_id"],
            },
        ),
        FunctionDeclaration(
            name="search_graph",
            description="Semantic search across the client's skill graph. "
                        "Use when you don't know which node has the answer.",
            parameters={
                "type": "object",
                "properties": {
                    "client_id": {"type": "string", "description": "The client identifier"},
                    "query": {"type": "string", "description": "Natural language search query"},
                },
                "required": ["client_id", "query"],
            },
        ),
    ]

    return [Tool(function_declarations=declarations)]


async def run_text_conversation(
    client_id: str,
    message: str,
    history: list[dict] | None = None,
) -> dict:
    """Run a single turn of text conversation with the Handoff agent.

    This is the R1 text-mode agent. It uses Gemini with function calling
    to navigate the skill graph and provide grounded answers.

    Args:
        client_id: Client identifier for graph traversal.
        message: User's message.
        history: Previous conversation turns (optional).

    Returns:
        Dict with agent response, tool calls made, and nodes visited.
    """
    client = genai.Client(api_key=config.gemini_api_key)
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

    gen_config = GenerateContentConfig(
        system_instruction=HANDOFF_SYSTEM_PROMPT,
        temperature=0.3,
        max_output_tokens=4096,
        tools=tools,
    )

    tool_calls_log = []
    nodes_visited = []
    max_tool_rounds = 8  # Prevent infinite tool-calling loops

    for round_num in range(max_tool_rounds):
        response = await client.aio.models.generate_content(
            model=config.graph_gen_model,  # Using 3.1 Pro for text agent too
            contents=contents,
            config=gen_config,
        )

        # Check if the response has function calls
        candidate = response.candidates[0]
        has_function_calls = False

        for part in candidate.content.parts:
            if part.function_call:
                has_function_calls = True
                fc = part.function_call
                fn_name = fc.name
                fn_args = dict(fc.args) if fc.args else {}

                # Inject client_id if not provided
                if "client_id" not in fn_args:
                    fn_args["client_id"] = client_id

                print(f"[AGENT] Tool call: {fn_name}({fn_args})")
                tool_calls_log.append({"tool": fn_name, "args": fn_args})

                # Execute the tool
                tool_fn = TOOL_FUNCTIONS.get(fn_name)
                if tool_fn:
                    result = tool_fn(**fn_args)
                    # Track visited nodes
                    try:
                        result_data = json.loads(result)
                        if "node_id" in result_data:
                            nodes_visited.append(result_data["node_id"])
                    except (json.JSONDecodeError, KeyError):
                        pass
                else:
                    result = json.dumps({"error": f"Unknown tool: {fn_name}"})

                # Add the function call and response to conversation
                contents.append(candidate.content)
                contents.append(
                    Content(
                        role="user",
                        parts=[Part.from_function_response(name=fn_name, response={"result": result})],
                    )
                )
                break  # Process one function call at a time

        if not has_function_calls:
            # Model returned a text response — we're done
            agent_response = candidate.content.parts[0].text if candidate.content.parts else ""
            return {
                "response": agent_response,
                "tool_calls": tool_calls_log,
                "nodes_visited": nodes_visited,
                "rounds": round_num + 1,
            }

    # Exhausted tool rounds
    return {
        "response": "I've navigated through several nodes but need more specific guidance. Could you ask a more targeted question?",
        "tool_calls": tool_calls_log,
        "nodes_visited": nodes_visited,
        "rounds": max_tool_rounds,
        "warning": "Max tool call rounds reached",
    }
