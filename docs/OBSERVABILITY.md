# 🔬 Level 5 Agent Observability & Telemetry

Creating a production-grade voice agent through the **Synapse Hub** requires moving past simple API requests into deep telemetry.

## 1. Request Telemetry (`core/telemetry.py`)

Every interaction with the Voice Agent is decorated with advanced metrics capture:

- **Token Tracking**: We capture exactly how many Input, Output, and Total tokens are consumed across both the Generator endpoints and the Live WebRTC session.
- **Latency Tracking**: End-to-end round trip time (RTT) is recorded for all tool executions. If the semantic vector search takes longer than `200ms`, an explicit warning is logged to prompt performance tuning.

```json
// Example Telemetry Span
{
  "trace_id": "8489aabc-3391",
  "event": "tool_execution",
  "tool_name": "search_graph",
  "duration_ms": 112,
  "tokens": {
    "prompt": 832,
    "completion": 45
  }
}
```

## 2. Multi-Agent Tracing

Because the Graph Generator utilizes multiple models in an asynchronous loop, tracing is critical. We use standard nested Job IDs to track state boundaries in GCP Cloud Logging:

1. `Job[a1b2] > Status: Extraction_Transcript`
2. `Job[a1b2] > Status: Extraction_Contract`
3. `Job[a1b2] > Status: Generative_Pass`
4. `Job[a1b2] > Status: Review_Critique_Pass`

If a generation job fails on the critique pass, the exact output of the generator is preserved in the trace for debugging, preventing the "black box" failure typical of chained LLM interactions.

## 3. Tool Function Logging

The Gemini Live model has access to external APIs. Every time the model decides to invoke `follow_link` or `escalate_risk`, the raw arguments it chose to map are intercepted by the Python middleware and logged into the `stdout` stream (which maps directly into GCP Cloud Logging), ensuring complete auditability of the AI's autonomous decisions.
