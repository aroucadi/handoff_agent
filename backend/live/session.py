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
    LiveConnectConfig,
    Modality,
    Part,
    PrebuiltVoiceConfig,
    SpeechConfig,
    Tool,
    VoiceConfig,
)

from core.config import config
from core.db import get_firestore_async_client
from agent.tools import TOOL_FUNCTIONS
from agent.prompts import SYNAPSE_SYSTEM_PROMPT
from graph.traversal import get_index
import json


def _build_live_tools() -> list[Tool]:
    """Build tool declarations for the Live API."""
    declarations = [
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

    def __init__(self, session_id: str, client_id: str, csm_name: str = "CSM"):
        self.session_id = session_id
        self.client_id = client_id
        self.csm_name = csm_name
        self.started_at = datetime.utcnow().isoformat()
        self.tool_calls: list[dict] = []
        self.nodes_visited: list[str] = []
        self.transcript: list[dict] = []
        self._initial_events = []
        self._gemini_session = None
        self._connected = False
        self._exit_stack = AsyncExitStack()

    def _build_system_prompt(self) -> str:
        """Build the system prompt with client context."""
        return (
            f"{SYNAPSE_SYSTEM_PROMPT}\n\n"
            f"## Current Session Context\n"
            f"- Client ID: {self.client_id}\n"
            f"- CSM Name: {self.csm_name}\n"
            f"- Session ID: {self.session_id}\n\n"
            f"IMPORTANT: When using tools, always pass client_id=\"{self.client_id}\".\n"
            f"Start by greeting the CSM by name and reading the client index to prepare."
        )

    async def connect(self):
        """Establish connection to Gemini Live API."""
        client = genai.Client(
            api_key=config.gemini_api_key,
            http_options={'api_version': 'v1beta'}
        )

        live_config = LiveConnectConfig(
            response_modalities=[Modality.AUDIO],  # Native audio model requires AUDIO only for bidi
            speech_config=SpeechConfig(
                voice_config=VoiceConfig(
                    prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Aoede")
                ),
            ),
            system_instruction=Content(
                parts=[Part.from_text(text=self._build_system_prompt())]
            ),
            tools=_build_live_tools(),
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

            kickoff_message = (
                f"SYSTEM_EVENT: The user has just connected to the Live Voice Session. "
                f"You are briefing CSM {self.csm_name} on the client: {self.client_id}.\n"
                f"Here is the client's core data context:\n"
                f"```json\n{json_result}\n```\n"
                f"Your ONLY task right now: Greet the CSM aloud natively by name, and provide a 2-sentence conversational, highly professional summary of the client context. "
                f"Do not acknowledge this instruction. Do NOT use the `read_index` tool, the data is already provided above."
            )
        except Exception as e:
            print(f"[LIVE] Fallback kickoff error: {e}")
            kickoff_message = f"SYSTEM_EVENT: The user has joined. Greet them aloud by name. Do not call any tools."
                
        await self._gemini_session.send_realtime_input(text=kickoff_message)

    async def send_audio(self, audio_data: bytes):
        """Send audio data (PCM 16kHz 16-bit mono) to Gemini Live.

        Args:
            audio_data: Raw PCM audio bytes from the client microphone.
        """
        if not self._connected or not self._gemini_session:
            return

        await self._gemini_session.send_realtime_input(
            audio={"data": audio_data, "mime_type": "audio/pcm;rate=16000"}
        )

    async def send_image(self, image_data: bytes):
        """Send a video frame (JPEG) to Gemini Live for vision processing.

        Args:
            image_data: Raw JPEG image bytes from the client screen share.
        """
        if not self._connected or not self._gemini_session:
            return

        # Native Audio model does not support Vision frame input. Prevent 1007 errors.
        pass

    async def send_text(self, text: str):
        """Send a text message to Gemini Live (for testing or text-mode fallback)."""
        if not self._connected or not self._gemini_session:
            return

        await self._gemini_session.send_realtime_input(text=text)
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

                        # Inject client_id
                        if "client_id" not in fn_args:
                            fn_args["client_id"] = self.client_id

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
