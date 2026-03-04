"""Graph Generator — Node Generator.

Uses Gemini 2.5 Pro to generate real markdown skill graph nodes from extracted entities.
Each node follows the YAML frontmatter schema defined in the SYNAPSE PRD.
"""

from __future__ import annotations

import json
import asyncio
from datetime import date, datetime

from google import genai
from google.genai.types import GenerateContentConfig

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import config
from core.llm import generate_content_with_fallback

from core.db import get_firestore_client

# ── Dynamic Configuration ────────────────────────────────────────

def load_tenant_config(tenant_id: str) -> dict | None:
    """Load tenant-specific configuration from Firestore."""
    if not tenant_id:
        return None
    try:
        db = get_firestore_client()
        doc = db.collection("tenants").document(tenant_id).get()
        if doc.exists:
            return doc.to_dict()
    except Exception as e:
        print(f"[NODE_GEN] Warning: Failed to load tenant {tenant_id}: {e}")
    return None


NODE_GENERATION_PROMPT = """You are a skill graph architect for a B2B SaaS customer success platform called {brand_name}.

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
6. **Product Fit** (node_id: "{client_slug}-product-fit") — How purchased {brand_name} products map to client needs
7. **Kickoff Prep** (node_id: "{client_slug}-kickoff-prep") — CSM briefing notes for the first meeting
8. **Holistic Account History** (node_id: "{client_slug}-account-history") — An overarching synthesis of ALL deals for this account.

RULES:
- Every wikilink MUST be woven into prose, not standalone
- Cross-link to {brand_name} product nodes using: {product_links}.
- Cross-link to industry nodes using [[manufacturing-index]], [[tech-index]], [[financial-services-index]], etc.
- Each node MUST be independently useful — if the agent reads only this node, it should make sense
- Use REAL data from the extraction (including historical deals) — never fabricate facts not in the source data
- Include direct quotes from stakeholders where available

Return a JSON array of objects, each with "node_id" and "content" (the full markdown including YAML frontmatter).

CLIENT DATA:
"""

REVIEWER_PROMPT = """You are a strict QA Reviewer for a skill graph generation pipeline for {brand_name}.

Your job is to review the JSON array of draft markdown nodes provided below.
You must ensure:
1. Every node has valid YAML frontmatter exactly matching the schema.
2. Every [[wikilink]] in the prose resolves to a `node_id` that ACTUALLY EXISTS in the provided JSON array, or to one of these valid static nodes: {product_links}, [[manufacturing-index]], [[tech-index]], [[financial-services-index]].
3. If a wikilink points to a node that does not exist, REMOVE the wikilink brackets but keep the text.
4. The output must be valid JSON.

You must not change the core facts or meaning of the nodes. Only fix formatting, links, and schema issues.

Format your response as a pure JSON array with no markdown code blocks outside of the JSON payload itself.

DRAFT NODES:
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
    tenant_id: str | None = None,
) -> list[dict]:
    """Generate client skill graph nodes using Gemini 3.1 Pro.

    Args:
        client_id: Unique client identifier (used in node_ids and paths).
        company_name: Full company name.
        industry: Industry vertical.
        crm_data: Structured CRM data from crm_extractor.
        transcript_data: Structured transcript data from transcript_extractor (optional).
        contract_data: Structured contract data from contract_extractor (optional).
        tenant_id: Hub tenant ID to pull custom branding and product catalog.

    Returns:
        List of dicts with "node_id" and "content" for each generated node.
    """
    client_slug = _build_client_slug(company_name)
    today = date.today().isoformat()

    # Load Tenant Config if available
    tenant_config = load_tenant_config(tenant_id)
    brand_name = tenant_config.get("brand_name", "ClawdView") if tenant_config else "ClawdView"
    
    # Extract product node IDs from tenant catalog, or fall back to defaults
    if tenant_config and tenant_config.get("products"):
        product_list = [f"[[{p['node_id']}]]" for p in tenant_config["products"] if p.get('node_id')]
        product_list.append("[[implementation-patterns]]")
    else:
        product_list = ["[[clawdview-portfolios]]", "[[clawdview-agileplace]]", "[[clawdview-ppm-pro]]", "[[clawdview-hub]]", "[[implementation-patterns]]"]
    
    product_links_str = ", ".join(product_list)

    # Build the combined data payload for Gemini
    combined_data = {
        "client_id": client_id,
        "client_slug": client_slug,
        "company_name": company_name,
        "brand_name": brand_name,
        "industry": industry,
        "today": today,
        "crm_data": crm_data,
    }
    if transcript_data:
        combined_data["transcript_extraction"] = transcript_data
    if contract_data:
        combined_data["contract_extraction"] = contract_data

    # Format prompts with dynamic values
    prompt = NODE_GENERATION_PROMPT.format(
        brand_name=brand_name,
        client_id=client_id,
        client_slug=client_slug,
        industry=industry,
        today=today,
        product_links=product_links_str
    )
    prompt += json.dumps(combined_data, indent=2, default=str)

    # Update reviewer prompt
    reviewer_prompt_base = REVIEWER_PROMPT.format(
        brand_name=brand_name,
        product_links=product_links_str
    )

    try:
        gen_config = GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
            max_output_tokens=16384,  # Nodes can be long
        )
        
        from core.telemetry import record_trace
        start_gen_time = datetime.utcnow()
        
        raw_text = await generate_content_with_fallback(
            contents=prompt,
            gen_config=gen_config,
            primary_model=config.gen_model,
            fallback_model=config.fallback_model,
        )
        end_gen_time = datetime.utcnow()
        
        asyncio.create_task(
            record_trace(
                agent_name="node_generator_draft",
                job_id=f"generate-{client_id}",
                start_time=start_gen_time,
                end_time=end_gen_time,
                client_id=client_id,
            )
        )
        
        if not raw_text:
            return []
            
        # --- AGENT 2: The Reviewer ---
        print("[NODE_GEN] Generation complete. Starting Reviewer Agent pass...")
        reviewer_prompt = reviewer_prompt_base + raw_text
        
        start_rev_time = datetime.utcnow()
        reviewed_text = await generate_content_with_fallback(
            contents=reviewer_prompt,
            gen_config=gen_config,
            primary_model=config.gen_model,
            fallback_model=config.fallback_model,
        )
        end_rev_time = datetime.utcnow()
        
        asyncio.create_task(
            record_trace(
                agent_name="node_generator_reviewer",
                job_id=f"review-{client_id}",
                start_time=start_rev_time,
                end_time=end_rev_time,
                client_id=client_id,
            )
        )
        if not reviewed_text:
            reviewed_text = raw_text # Fallback to unreviewed if reviewer fails
            
    except Exception as e:
        print(f"[NODE_GEN] Pipeline failed: {e}")
        return []

    # Parse JSON array of nodes
    try:
        nodes = json.loads(reviewed_text)
    except json.JSONDecodeError:
        if "```json" in reviewed_text:
            json_str = reviewed_text.split("```json")[1].split("```")[0].strip()
            nodes = json.loads(json_str)
        elif "```" in reviewed_text:
            json_str = reviewed_text.split("```")[1].split("```")[0].strip()
            nodes = json.loads(json_str)
        else:
            # Fallback parsing attempt
            try:
                nodes = json.loads(raw_text)
            except Exception:
                raise ValueError(f"Failed to parse node generation response: {reviewed_text[:500]}")

    if not isinstance(nodes, list):
        nodes = [nodes]

    return nodes
