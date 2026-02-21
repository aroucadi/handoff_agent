"""Graph Generator — Transcript Extractor.

Uses Gemini 3.1 Pro to extract structured entities from sales call transcripts.
Returns JSON with stakeholders, pain points, promises, risks, and objections.
"""

from __future__ import annotations

import json
from google import genai
from google.genai.types import GenerateContentConfig

from config import config

EXTRACTION_PROMPT = """You are an expert at analyzing B2B SaaS sales call transcripts.

Extract the following entities from this sales call transcript. Return ONLY valid JSON with this exact structure:

{
  "stakeholders": [
    {
      "name": "Full Name",
      "title": "Job Title",
      "role": "champion | economic_buyer | technical_evaluator | end_user | blocker",
      "pain_points": ["specific pain point mentioned"],
      "commitments": ["specific commitment or expectation stated"],
      "communication_style": "brief personality note for CSM",
      "key_quotes": ["verbatim quote that reveals their priority"]
    }
  ],
  "deal_context": {
    "products_purchased": ["product names"],
    "total_deal_value": "dollar amount if mentioned",
    "timeline_expectations": "go-live timeline discussed",
    "success_criteria": ["specific measurable outcomes mentioned"]
  },
  "promises_made": [
    {
      "promise": "what was committed",
      "by_whom": "who made the promise",
      "to_whom": "who was it made to",
      "timeline": "when it should happen"
    }
  ],
  "risks_identified": [
    {
      "risk": "description of the risk",
      "severity": "high | medium | low",
      "source": "who raised it or where it was identified",
      "unresolved": true
    }
  ],
  "objections_raised": [
    {
      "objection": "the concern stated",
      "by_whom": "who raised it",
      "resolved": false,
      "resolution": "how it was addressed, if at all"
    }
  ],
  "action_items": [
    {
      "action": "what needs to happen",
      "owner": "who is responsible",
      "deadline": "when, if mentioned"
    }
  ]
}

IMPORTANT:
- Extract ONLY information explicitly stated in the transcript
- Do NOT infer or hallucinate information not present
- Use exact quotes where possible
- If a field has no data, use an empty array or null

TRANSCRIPT:
"""


async def extract_from_transcript(transcript: str) -> dict:
    """Extract structured entities from a sales call transcript using Gemini 3.1 Pro.

    Args:
        transcript: Raw sales call transcript text.

    Returns:
        Dictionary with extracted entities (stakeholders, risks, promises, etc.)
    """
    client = genai.Client(api_key=config.gemini_api_key)

    try:
        response = await client.aio.models.generate_content(
            model=config.gen_model,
            contents=EXTRACTION_PROMPT + transcript,
            config=GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,  # Low temperature for factual extraction
                max_output_tokens=8192,
            ),
        )
    except Exception as e:
        print(f"[TRANSCRIPT] Primary model failed ({e}), trying fallback model...")
        response = await client.aio.models.generate_content(
            model=config.fallback_model,
            contents=EXTRACTION_PROMPT + transcript,
            config=GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                max_output_tokens=8192,
            ),
        )

    raw_text = response.text.strip()

    # Parse JSON response
    try:
        extracted = json.loads(raw_text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code block if model wrapped it
        if "```json" in raw_text:
            json_str = raw_text.split("```json")[1].split("```")[0].strip()
            extracted = json.loads(json_str)
        elif "```" in raw_text:
            json_str = raw_text.split("```")[1].split("```")[0].strip()
            extracted = json.loads(json_str)
        else:
            raise ValueError(f"Failed to parse extraction response as JSON: {raw_text[:500]}")

    return extracted
