"""Graph Generator — Node Generator.

Uses Gemini 3.1 Pro to generate real markdown skill graph nodes from extracted entities.
Each node follows the YAML frontmatter schema defined in the HANDOFF PRD.
"""

from __future__ import annotations

import json
from datetime import date

from google import genai
from google.genai.types import GenerateContentConfig

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import config
from core.llm import generate_content_with_fallback

NODE_GENERATION_PROMPT = """You are a skill graph architect for a B2B SaaS customer success platform.

Given the extracted data below, generate a set of interconnected markdown nodes for a client skill graph.
Each node must follow this EXACT format:

```
---
title: "Human-readable title"
node_id: "kebab-case-unique-id"
client_id: "{client_id}"
layer: "client"
stage: ["onboarding"]
domain: "{industry}"
links:
  - other-node-id
  - another-node-id
description: "One sentence describing what is in this node and WHEN the agent should read it."
last_updated: "{today}"
---

[Markdown content: 150-400 words, with [[wikilinks]] woven into prose]
```

Generate these specific nodes:
1. **Client Index** (node_id: "{client_slug}-index") — MOC linking to all other client nodes
2. **Stakeholder Map** (node_id: "{client_slug}-stakeholder-map") — All contacts with roles, styles, priorities
3. **Risk Flags** (node_id: "{client_slug}-risk-flags") — Every identified risk with severity and mitigation
4. **Success Metrics** (node_id: "{client_slug}-success-metrics") — Measurable targets with baselines and timelines
5. **Implementation Plan** (node_id: "{client_slug}-implementation-plan") — Recommended approach based on deal details
6. **Product Fit** (node_id: "{client_slug}-product-fit") — How purchased products map to client needs
7. **Kickoff Prep** (node_id: "{client_slug}-kickoff-prep") — CSM briefing notes for the first meeting
8. **Deal History** (node_id: "{client_slug}-deal-history") — Key moments from the sales process

RULES:
- Every wikilink MUST be woven into prose, not standalone
- Cross-link to static product nodes using [[cpq-module]], [[revenue-cloud]], [[implementation-patterns]], etc.
- Cross-link to industry nodes using [[manufacturing-index]], [[manufacturing-cpq-complexity]], etc.
- Each node MUST be independently useful — if the agent reads only this node, it should make sense
- Use REAL data from the extraction — never fabricate facts not in the source data
- Include direct quotes from stakeholders where available

Return a JSON array of objects, each with "node_id" and "content" (the full markdown including YAML frontmatter).

CLIENT DATA:
"""


def _build_client_slug(company_name: str) -> str:
    """Convert company name to kebab-case slug."""
    return company_name.lower().replace(" ", "-").replace(".", "").replace(",", "")


async def generate_client_nodes(
    client_id: str,
    company_name: str,
    industry: str,
    crm_data: dict,
    transcript_data: dict | None = None,
    contract_data: dict | None = None,
) -> list[dict]:
    """Generate client skill graph nodes using Gemini 3.1 Pro.

    Args:
        client_id: Unique client identifier (used in node_ids and paths).
        company_name: Full company name.
        industry: Industry vertical.
        crm_data: Structured CRM data from crm_extractor.
        transcript_data: Structured transcript data from transcript_extractor (optional).
        contract_data: Structured contract data from contract_extractor (optional).

    Returns:
        List of dicts with "node_id" and "content" for each generated node.
    """
    client_slug = _build_client_slug(company_name)
    today = date.today().isoformat()

    # Build the combined data payload for Gemini
    combined_data = {
        "client_id": client_id,
        "client_slug": client_slug,
        "company_name": company_name,
        "industry": industry,
        "today": today,
        "crm_data": crm_data,
    }
    if transcript_data:
        combined_data["transcript_extraction"] = transcript_data
    if contract_data:
        combined_data["contract_extraction"] = contract_data

    prompt = NODE_GENERATION_PROMPT.replace("{client_id}", client_id)
    prompt = prompt.replace("{client_slug}", client_slug)
    prompt = prompt.replace("{industry}", industry)
    prompt = prompt.replace("{today}", today)
    prompt += json.dumps(combined_data, indent=2, default=str)

    try:
        gen_config = GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
            max_output_tokens=16384,  # Nodes can be long
        )
        
        raw_text = await generate_content_with_fallback(
            contents=prompt,
            gen_config=gen_config,
            primary_model=config.gen_model,
            fallback_model=config.fallback_model,
        )
        if not raw_text:
            return []
    except Exception as e:
        print(f"[NODE_GEN] Generation failed: {e}")
        return []

    # Parse JSON array of nodes
    try:
        nodes = json.loads(raw_text)
    except json.JSONDecodeError:
        if "```json" in raw_text:
            json_str = raw_text.split("```json")[1].split("```")[0].strip()
            nodes = json.loads(json_str)
        elif "```" in raw_text:
            json_str = raw_text.split("```")[1].split("```")[0].strip()
            nodes = json.loads(json_str)
        else:
            raise ValueError(f"Failed to parse node generation response: {raw_text[:500]}")

    if not isinstance(nodes, list):
        nodes = [nodes]

    return nodes
