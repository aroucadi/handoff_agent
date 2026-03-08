"""Synapse Backend — Gemini Live Session Handler.

Manages real-time voice sessions using the Gemini Multimodal Live API
(gemini-2.5-flash-native-audio-preview). Handles bidirectional audio
streaming with tool calling for graph traversal during conversations.
"""

from __future__ import annotations

import asyncio
import base64
import json
import uuid
from datetime import datetime
from contextlib import AsyncExitStack

from google import genai
from google.genai.types import (
    Content,
    FunctionDeclaration,
    FunctionResponse,
    GoogleSearch,
    LiveConnectConfig,
    Modality,
    Part,
    PrebuiltVoiceConfig,
    SpeechConfig,
    Tool,
    VoiceConfig,
    ActivityEnd,
)

from core.config import config
from core.db import get_firestore_async_client
from agent.tools import TOOL_FUNCTIONS
from agent.prompts import get_role_prompt, get_role_config
from graph.traversal import get_index
import json


def _build_live_tools() -> list[Tool]:
    """Build tool declarations for the Live API.
    
    Includes: legacy graph tools, structured entity tools, and output generators.
    """
    declarations = [
        # ── Structured Graph Tools (Primary) ──
        FunctionDeclaration(
            name="graph_overview",
            description="Get a high-level overview of the client's knowledge graph. Use FIRST to understand available knowledge.",
            parameters={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "client_id": {"type": "string"},
                },
                "required": ["tenant_id", "client_id"],
            },
        ),
        FunctionDeclaration(
            name="get_entity",
            description="Retrieve a specific entity and its connections from the knowledge graph.",
            parameters={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "client_id": {"type": "string"},
                    "entity_id": {"type": "string"},
                },
                "required": ["tenant_id", "client_id", "entity_id"],
            },
        ),
        FunctionDeclaration(
            name="get_entities_by_type",
            description="Get all entities of a specific type (e.g., Risk, Contact, Product).",
            parameters={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "client_id": {"type": "string"},
                    "entity_type": {"type": "string"},
                },
                "required": ["tenant_id", "client_id", "entity_type"],
            },
        ),
        FunctionDeclaration(
            name="traverse_graph",
            description="Multi-hop graph traversal from an entity.",
            parameters={
                "type": "object",
                "properties": {
                    "tenant_id": {"type": "string"},
                    "client_id": {"type": "string"},
                    "entity_id": {"type": "string"},
                    "edge_type": {"type": "string"},
                    "max_hops": {"type": "integer"},
                },
                "required": ["tenant_id", "client_id", "entity_id"],
            },
        ),
        FunctionDeclaration(
            name="search_entities",
            description="Semantic search across knowledge graph entities. "
                        "Optionally filter by entity type.",
            parameters={
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "query": {"type": "string"},
                    "entity_type": {"type": "string", "description": "Optional type filter"},
                },
                "required": ["client_id", "query"],
            },
        ),
        FunctionDeclaration(
            name="risk_profile",
            description="Get comprehensive risk profile: all risks with severity breakdown and derisking strategies.",
            parameters={
                "type": "object",
                "properties": {"client_id": {"type": "string"}},
                "required": ["client_id"],
            },
        ),
        FunctionDeclaration(
            name="product_knowledge",
            description="Get product knowledge: products, features, limitations, and KB articles.",
            parameters={
                "type": "object",
                "properties": {"client_id": {"type": "string"}},
                "required": ["client_id"],
            },
        ),
        # ── Output Generation Tools ──
        FunctionDeclaration(
            name="generate_briefing",
            description="Generate a pre-meeting briefing summary from the knowledge graph.",
            parameters={
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "csm_name": {"type": "string", "description": "CSM name for personalization"},
                },
                "required": ["client_id"],
            },
        ),
        FunctionDeclaration(
            name="generate_action_plan",
            description="Generate a post-session action plan with prioritized items.",
            parameters={
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "meeting_notes": {"type": "string", "description": "Optional session notes"},
                },
                "required": ["client_id"],
            },
        ),
        FunctionDeclaration(
            name="generate_transcript",
            description="Generate a role-based script (sales, support, QBR, renewal, onboarding, discovery). "
                        "Use when user asks for a transcript, script, or talking points.",
            parameters={
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "transcript_type": {
                        "type": "string",
                        "enum": ["sales_script", "support_script", "qbr_prep",
                                 "renewal_script", "onboarding_guide", "discovery_questions"],
                    },
                    "user_role": {"type": "string", "description": "User role (AE, CSM, Support Agent)"},
                    "additional_context": {"type": "string", "description": "Extra context or notes"},
                },
                "required": ["client_id", "transcript_type"],
            },
        ),
        # ── Legacy Tools (backward compat) ──
        FunctionDeclaration(
            name="read_index",
            description="Read the index/table-of-contents node for a skill graph layer. ",
            parameters={
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "layer": {"type": "string", "enum": ["client", "product", "industry"]},
                },
                "required": ["client_id"],
            },
        ),
        FunctionDeclaration(
            name="follow_link",
            description="Navigate to a specific node in the skill graph. "
                        "Use when a [[wikilink]] is relevant to the question. "
                        "Set sections_only to true to safely preview long nodes.",
            parameters={
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "node_id": {"type": "string"},
                    "sections_only": {"type": "boolean"},
                },
                "required": ["client_id", "node_id"],
            },
        ),
        FunctionDeclaration(
            name="search_graph",
            description="Semantic search across the skill graph. "
                        "Use when you don't know which node has the answer.",
            parameters={
                "type": "object",
                "properties": {
                    "client_id": {"type": "string"},
                    "query": {"type": "string"},
                },
                "required": ["client_id", "query"],
            },
        ),
    ]
    return [Tool(function_declarations=declarations)]


class LiveSession:
    """Manages a single Gemini Live voice session.

    Connects to the Gemini Multimodal Live API, handles bidirectional
    audio streaming, tool calls, and session state tracking.
    """

    def __init__(self, session_id: str, client_id: str, csm_name: str = "CSM",
                 deal_id: str | None = None, role: str = "csm",
                 tenant_id: str | None = None, brand_name: str = "ClawdView"):
        self.session_id = session_id
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.brand_name = brand_name
        self.csm_name = csm_name
        self.deal_id = deal_id
        self.role = role
        self.started_at = datetime.utcnow().isoformat()
        self.tool_calls: list[dict] = []
        self.nodes_visited: list[str] = []
        self.transcript: list[dict] = []
        self._initial_events = []
        self._gemini_session = None
        self._connected = False
        self._exit_stack = AsyncExitStack()

    def _build_system_prompt(self) -> str:
        """Build the system prompt dynamically based on role + deal context."""
        role_config = get_role_config(self.role, brand_name=self.brand_name)
        role_prompt = get_role_prompt(self.role, brand_name=self.brand_name)

        deal_context = ""
        if self.deal_id:
            deal_context = (
                f"\n## Deal Focus\n"
                f"- **Primary Deal ID**: {self.deal_id}\n"
                f"- This briefing is about a SPECIFIC DEAL. Your primary focus should be on this deal's data.\n"
                f"- Account-level history (other deals) is SUPPLEMENTARY context.\n"
            )

        # Add role-aware data focus hints
        data_focus = role_config.get('data_focus', [])
        focus_hint = ""
        if data_focus:
            focus_hint = (
                f"\n## Priority Topics\n"
                f"When navigating the graph, prioritize these topics: {', '.join(data_focus)}.\n"
            )

        return (
            f"{role_prompt}\n\n"
            f"## Multimodal Awareness (CRITICAL)\n"
            f"- **VISUAL INPUT**: You are receiving a high-frequency live stream of the user's screen (Vision). \n"
            f"- **GROUNDING**: If the user asks 'What do you see?' or refers to 'this' while showing a document/CRM page, analyze the visual frames to give a grounded answer.\n"
            f"- **AUDIO INPUT**: You are in a real-time voice session. Speak naturally, be concise, and handle interruptions (barge-in) gracefully.\n\n"
            f"## Current Session Context\n"
            f"- Client ID: {self.client_id}\n"
            f"- User Name: {self.csm_name}\n"
            f"- Session ID: {self.session_id}\n"
            f"- Tenant ID: {self.tenant_id}\n"
            f"- Brand Filter: {self.brand_name}\n"
            f"{deal_context}"
            f"{focus_hint}\n"
            f"IMPORTANT: When using tools, always pass client_id=\"{self.client_id}\".\n"
            f"CRITICAL OVERRIDE: If the user sends a TEXT message, you MUST still respond ALOUD using VOICE (Audio Modality).\n"
            f"Start by greeting {self.csm_name} naturally (first name ONLY). You are {role_config['greeting_style']}."
        )

    async def connect(self):
        """Establish connection to Gemini Live API."""
        client = genai.Client(
            vertexai=True,
            project=config.project_id,
            location=config.region
        )

        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],  # Native audio model strictly allows ONE response modality
            speech_config=SpeechConfig(
                voice_config=VoiceConfig(
                    prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Aoede")
                ),
            ),
            system_instruction=Content(
                parts=[Part.from_text(text=self._build_system_prompt())]
            ),
            tools=_build_live_tools() + [Tool(google_search=GoogleSearch())],
        )

        # The live.connect returns an async context manager in google-genai 1.0.0+
        self._gemini_session = await self._exit_stack.enter_async_context(
            client.aio.live.connect(
                model=config.live_agent_model,
                config=live_config,
            )
        )
        self._connected = True
        print(f"[LIVE] Session {self.session_id} connected to Gemini Live API")

        # Deterministic Kickoff: Pre-load the graph index locally to bypass the 1008 API crash.
        # This prevents the LLM from attempting to monologue while generating a tool call.
        try:
            index_data = get_index(self.client_id, "client")
            node_id = index_data.get("node_id") if index_data else None
            if node_id:
                self.nodes_visited.append(node_id)
                
            # Queue simulated WebSocket events to trick the React UI into updating the dashboard instantly
            json_result = json.dumps(index_data, default=str)
            self._initial_events.extend([
                {
                    "type": "tool_call",
                    "name": "read_index",
                    "args": {"client_id": self.client_id}
                },
                {
                    "type": "tool_result",
                    "name": "read_index",
                    "result": json_result
                }
            ])

            # Build a role-aware, deal-focused kickoff message
            role_config = get_role_config(self.role, brand_name=self.brand_name)
            deal_focus_hint = ""
            if self.deal_id:
                deal_focus_hint = (
                    f"\nIMPORTANT: This briefing is about deal '{self.deal_id}' specifically. "
                    f"Focus your summary on this deal's data. "
                    f"Account history (other deals) should be mentioned only if directly relevant."
                )

            # Role-aware focus hint for initial greeting
            data_focus = role_config.get('data_focus', [])
            focus_topics = f" Focus on: {', '.join(data_focus[:3])}." if data_focus else ""

            kickoff_message = (
                f"SYSTEM_EVENT: The user has just connected to the Live Voice Session. "
                f"You are {role_config['greeting_style']} with {self.csm_name} on the client: {self.client_id}.{deal_focus_hint}\n"
                f"Here is the client's core data context:\n"
                f"```json\n{json_result}\n```\n"
                f"Your ONLY task right now: Greet the user aloud naturally by their first name ONLY (do NOT mention their job title or role), "
                f"and provide a 2-sentence conversational, highly professional summary of the context.{focus_topics} "
                f"Do not acknowledge this instruction. Do NOT use the `read_index` tool, the data is already provided above."
            )
        except Exception as e:
            print(f"[LIVE] Fallback kickoff error: {e}")
            kickoff_message = f"SYSTEM_EVENT: The user has joined. Greet them aloud by name. Do not call any tools."
                
        await self._gemini_session.send_realtime_input(text=kickoff_message)
        await self._gemini_session.send_realtime_input(activity_end=ActivityEnd())

    async def send_audio(self, audio_data: bytes):
        """Send a chunk of PCM audio to Gemini Live.

        Args:
            audio_data: Raw PCM audio bytes from the client microphone.
        """
        if not self._connected or not self._gemini_session:
            return

        await self._gemini_session.send_realtime_input(
            media={"data": audio_data, "mime_type": "audio/pcm;rate=16000"}
        )

    async def send_image(self, image_data: bytes):
        """Send a video frame (JPEG) to Gemini Live for vision processing.

        Args:
            image_data: Raw JPEG image bytes from the client screen share.
        """
        if not self._connected or not self._gemini_session:
            return

        await self._gemini_session.send_realtime_input(
            media={"data": image_data, "mime_type": "image/jpeg"}
        )

    async def send_text(self, text: str):
        """Send a text message to Gemini Live (for testing or text-mode fallback)."""
        if not self._connected or not self._gemini_session:
            return

        # gemini-live-2.5-flash natively supports text interruption via the live socket.
        await self._gemini_session.send_realtime_input(text=text)
        await self._gemini_session.send_realtime_input(activity_end=ActivityEnd())
        
        self.transcript.append({
            "role": "user",
            "text": text,
            "timestamp": datetime.utcnow().isoformat(),
        })

    async def receive_responses(self):
        """Async generator that yields responses from Gemini Live.

        Yields dicts with one of:
        - {"type": "audio", "data": base64_audio}
        - {"type": "text", "text": "..."}
        - {"type": "tool_call", "name": "...", "args": {...}}
        - {"type": "tool_result", "name": "...", "result": "..."}
        - {"type": "turn_complete"}
        - {"type": "interrupted"}
        """
        if not self._gemini_session:
            return

        # Yield any synthetic events (like the pre-cognitive graph load) to the UI first
        while self._initial_events:
            yield self._initial_events.pop(0)

        try:
            while True:
                try:
                    async for response in self._gemini_session.receive():
                        # Handle server content (audio/text responses)
                        if response.server_content:
                            sc = response.server_content

                            if sc.interrupted:
                                yield {"type": "interrupted"}
                                continue

                            if sc.model_turn and sc.model_turn.parts:
                                for part in sc.model_turn.parts:
                                    if part.inline_data:
                                        # Audio response
                                        audio_b64 = base64.b64encode(part.inline_data.data).decode()
                                        yield {
                                            "type": "audio",
                                            "data": audio_b64,
                                            "mime_type": part.inline_data.mime_type or "audio/pcm",
                                        }
                                    elif part.text:
                                        # Text response (thinking/transcript - suppressed from UI per user request)
                                        self.transcript.append({
                                            "role": "agent",
                                            "text": part.text,
                                            "timestamp": datetime.utcnow().isoformat(),
                                        })
                                        # Do not yield text to UI in Voice Mode
                                        yield {"type": "text", "text": part.text}

                            if sc.turn_complete:
                                yield {"type": "turn_complete"}

                        # Handle tool calls
                        if response.tool_call:
                            for fc in response.tool_call.function_calls:
                                fn_name = fc.name
                                fn_args = dict(fc.args) if fc.args else {}

                                # Scoping: Inject context if missing
                                if "tenant_id" not in fn_args:
                                    fn_args["tenant_id"] = self.tenant_id
                                if "client_id" not in fn_args:
                                    fn_args["client_id"] = self.client_id
                                if "account_id" not in fn_args:
                                    fn_args["account_id"] = self.client_id

                                print(f"[LIVE] Tool call: {fn_name}({fn_args})")
                                self.tool_calls.append({
                                    "tool": fn_name,
                                    "args": fn_args,
                                    "timestamp": datetime.utcnow().isoformat(),
                                })

                                yield {
                                    "type": "tool_call",
                                    "name": fn_name,
                                    "args": fn_args,
                                }

                                # Execute the tool
                                tool_fn = TOOL_FUNCTIONS.get(fn_name)
                                if tool_fn:
                                    # Handle both async and sync tools in the live loop
                                    if asyncio.iscoroutinefunction(tool_fn):
                                        result = await tool_fn(**fn_args)
                                    else:
                                        result = tool_fn(**fn_args)
                                    # Track visited nodes
                                    try:
                                        result_data = json.loads(result)
                                        if "node_id" in result_data:
                                            self.nodes_visited.append(result_data["node_id"])
                                            # Forward node_id in the fn_args so the tool_result event can capture it if needed
                                            fn_args["_node_id"] = result_data["node_id"]
                                    except (json.JSONDecodeError, KeyError):
                                        pass
                                else:
                                    result = json.dumps({"error": f"Unknown tool: {fn_name}"})

                                # Send tool result back to Gemini Live using dict for serialization safety
                                # Use the specific send_tool_response method to avoid 1008 policy validation errors
                                await self._gemini_session.send_tool_response(
                                    function_responses=[
                                        FunctionResponse(
                                            name=fn_name,
                                            id=fc.id,
                                            response={"result": result}
                                        )
                                    ]
                                )

                                yield {
                                    "type": "tool_result",
                                    "name": fn_name,
                                    "result": result, # Send full result to frontend so it can extract node_id 
                                }
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    print(f"[LIVE] Receive iteration yielded an inner loop break or error: {e}")
                    # If it's a normal disconnect from turn_complete, we loop again!
                    # BUT: prevent event loop exhaustion if we're in a tight error loop
                    await asyncio.sleep(0.1)
                    if not self._connected:
                        break
        except asyncio.CancelledError:
            print(f"[LIVE] Session {self.session_id} receive loop cancelled cleanly.")
            raise
        except Exception as e:
            print(f"[LIVE] Session {self.session_id} receive error: {e}")
            yield {"type": "error", "error": str(e)}

    async def disconnect(self):
        """Close the Gemini Live session and persist to Firestore."""
        try:
            await self._exit_stack.aclose()
        except Exception:
            pass
        self._gemini_session = None
        self._connected = False
        # Persist final state to Firestore
        await self.persist_to_firestore()

        # Fire off insights extraction in the background
        from live.insights import extract_and_save_session_insights
        asyncio.create_task(
            extract_and_save_session_insights(self.session_id, self.client_id, self.transcript)
        )

        print(f"[LIVE] Session {self.session_id} disconnected and persisted")

    async def persist_to_firestore(self):
        """Persist session state (transcript, tool calls, nodes visited) to Firestore.

        Called on disconnect and can be called periodically during conversation.
        Writes to: sessions/{session_id}
        """
        try:
            db = get_firestore_async_client()
            doc_ref = db.collection("sessions").document(self.session_id)
            await doc_ref.set({
                "session_id": self.session_id,
                "client_id": self.client_id,
                "csm_name": self.csm_name,
                "started_at": self.started_at,
                "ended_at": datetime.utcnow().isoformat(),
                "transcript": self.transcript,
                "tool_calls": self.tool_calls,
                "nodes_visited": list(set(self.nodes_visited)),
                "total_tool_calls": len(self.tool_calls),
                "total_messages": len(self.transcript),
            })
            print(f"[FIRESTORE] Persisted session {self.session_id}: "
                  f"{len(self.transcript)} messages, {len(self.tool_calls)} tool calls")
        except Exception as e:
            print(f"[FIRESTORE] Failed to persist session {self.session_id}: {e}")

    def get_history(self) -> dict:
        """Get the full session history."""
        return {
            "session_id": self.session_id,
            "client_id": self.client_id,
            "csm_name": self.csm_name,
            "started_at": self.started_at,
            "transcript": self.transcript,
            "tool_calls": self.tool_calls,
            "nodes_visited": list(set(self.nodes_visited)),
            "total_tool_calls": len(self.tool_calls),
        }

    @staticmethod
    async def get_history_from_firestore(session_id: str) -> dict | None:
        """Retrieve session history from Firestore (for sessions no longer in memory)."""
        try:
            db = get_firestore_async_client()
            doc = await db.collection("sessions").document(session_id).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            print(f"[FIRESTORE] Failed to read session {session_id}: {e}")
        return None
