"""Handoff Backend — Session Insights Extractor.

Extracts "learnings" from completed voice sessions using Gemini.
This fulfills Level 3 of the Agentic Architecture by extracting 
context and missing knowledge to improve future sessions.
"""

from datetime import datetime

from core.llm import generate_content_with_fallback
from core.db import get_firestore_async_client

INSIGHTS_PROMPT = """You are a RevOps Intelligence agent evaluating a recently concluded CSM voice briefing.
Your goal is to extract "learnings" and insights from the transcript to improve the system's memory.

Analyze the transcript and provide a JSON response with the following schema:
{
    "summary": "A 1-2 sentence summary of what the CSM talked about or asked for.",
    "missing_knowledge": ["List of specific items the CSM asked for that were NOT found in the tool responses"],
    "csm_sentiment": "positive|neutral|negative|frustrated",
    "follow_up_required": true/false
}

Focus heavily on the `missing_knowledge` field. If the agent had to say "I don't see that in the graph", 
record it here so the engineering team knows what data source needs to be added to the graph next.

Transcript:
"""


async def extract_and_save_session_insights(session_id: str, client_id: str, transcript: list) -> None:
    """Run LLM extraction on a transcript and save learnings to Firestore."""
    if not transcript or len(transcript) < 2:
        # Not enough data to extract meaningful insights
        return

    # Format transcript for the prompt
    formatted_transcript = ""
    for msg in transcript:
        time_str = msg.get("timestamp", "")
        formatted_transcript += f"[{time_str}] {msg.get('role', 'unknown').upper()}: {msg.get('text', '')}\n"

    prompt = INSIGHTS_PROMPT + formatted_transcript

    try:
        response_text = await generate_content_with_fallback(
            prompt=prompt,
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "summary": {"type": "STRING"},
                    "missing_knowledge": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    },
                    "csm_sentiment": {"type": "STRING"},
                    "follow_up_required": {"type": "BOOLEAN"},
                },
                "required": ["summary", "missing_knowledge", "csm_sentiment", "follow_up_required"]
            }
        )
        
        # Parse JSON and save to Firestore
        import json
        insights_data = json.loads(response_text)
        insights_data["session_id"] = session_id
        insights_data["client_id"] = client_id
        insights_data["extracted_at"] = datetime.utcnow().isoformat()

        db = get_firestore_async_client()
        await db.collection("client_insights").document(session_id).set(insights_data)
        print(f"[INSIGHTS] Successfully extracted learnings for session {session_id}")

    except Exception as e:
        print(f"[INSIGHTS] Failed to extract insights: {str(e)}")
