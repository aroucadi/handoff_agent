"""Handoff Backend — Telemetry Engine.

Provides Level 5 AI Observability.
A centralized service to log structured Agent execution traces
to Firestore. Used to track token usage, cost, latency, and tool paths.
"""

from __future__ import annotations

import logging
from datetime import datetime

from core.db import get_firestore_async_client

logger = logging.getLogger(__name__)


async def record_trace(
    agent_name: str,
    job_id: str,
    start_time: datetime,
    end_time: datetime,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    tools_used: list[dict] | None = None,
    client_id: str | None = None,
) -> None:
    """Write an agent execution trace to Firestore.

    Args:
        agent_name: Logical name of the agent executing (e.g., 'handoff_text_agent', 'node_reviewer')
        job_id: The session ID or graph generation job ID tracking this flow
        start_time: When the agent call began
        end_time: When the agent call completed
        prompt_tokens: Usage context tokens consumed
        completion_tokens: Usage generation tokens consumed
        tools_used: List of tools invoked during this run
        client_id: Optional client identifier for segmenting metrics
    """
    try:
        latency_ms = int((end_time - start_time).total_seconds() * 1000)

        trace_payload = {
            "agent_name": agent_name,
            "job_id": job_id,
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "tools_used": tools_used or [],
            "timestamp": end_time.isoformat(),
        }

        if client_id:
            trace_payload["client_id"] = client_id

        db = get_firestore_async_client()
        await db.collection("agent_traces").add(trace_payload)

        # Also print to stdout for standard cloud logging viewing
        print(f"[TRACE] {agent_name} | Latency: {latency_ms}ms | Cost: {(prompt_tokens + completion_tokens)} tokens")

    except Exception as e:
        # Strictly suppress errors so telemetry NEVER breaks the primary agent execution
        try:
            logger.error(f"[TELEMETRY] Failed to record trace for {agent_name}: {e}")
        except:
            pass
