"""Synapse Backend — Agent Generative Outputs.

Produces structured documents from the knowledge graph using Gemini:
  - Briefing summaries
  - Action plans
  - Risk reports
  - Recommendations
  - Handoff documents
"""

from __future__ import annotations

import json
from datetime import datetime

from google import genai
from google.genai.types import GenerateContentConfig

from core.config import config
from core.db import get_firestore_client
from graph.traversal import (
    get_graph_overview,
    get_risk_profile,
    get_product_knowledge,
    get_entities_by_type,
    traverse_from,
)

# ── Gemini Client ─────────────────────────────────────────────────

def _get_gemini_client():
    """Get a Gemini client for generation."""
    return genai.Client(vertexai=True, project=config.project_id, location=config.region)


def _generate(prompt: str, system: str = None) -> str:
    """Call Gemini to generate text content."""
    client = _get_gemini_client()
    gen_config = GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=4096,
    )
    if system:
        gen_config.system_instruction = system

    response = client.models.generate_content(
        model=config.generation_model,
        contents=prompt,
        config=gen_config,
    )
    return response.text


# ── Graph Data Collectors ─────────────────────────────────────────

def _collect_graph_context(client_id: str) -> dict:
    """Collect comprehensive graph data for document generation."""
    overview = get_graph_overview(client_id)
    risks = get_risk_profile(client_id)
    products = get_product_knowledge(client_id)
    contacts = get_entities_by_type(client_id, "Contact")
    deals = get_entities_by_type(client_id, "Deal")
    milestones = get_entities_by_type(client_id, "Milestone")
    success_metrics = get_entities_by_type(client_id, "SuccessMetric")
    commitments = get_entities_by_type(client_id, "Commitment")
    objections = get_entities_by_type(client_id, "Objection")

    return {
        "overview": overview,
        "risks": risks,
        "products": products,
        "contacts": contacts,
        "deals": deals,
        "milestones": milestones,
        "success_metrics": success_metrics,
        "commitments": commitments,
        "objections": objections,
    }


# ── Output Generators ────────────────────────────────────────────

async def generate_briefing(client_id: str, csm_name: str = "CSM") -> dict:
    """Generate a comprehensive briefing summary for a deal.

    Reads the full knowledge graph for a client and produces a structured
    briefing document covering all key aspects for a customer success meeting.

    Args:
        client_id: Client identifier.
        csm_name: Name of the CSM for personalization.

    Returns:
        Dict with title, content (markdown), and metadata.
    """
    ctx = _collect_graph_context(client_id)

    # Build the deal info from graph
    deal_info = ""
    for deal in ctx["deals"].get("entities", []):
        props = deal.get("properties", {})
        deal_info += f"- Deal: {props.get('name', 'Unknown')}, Value: ${props.get('value', 'N/A')}, Stage: {props.get('stage', 'N/A')}\n"

    prompt = f"""You are generating a pre-meeting briefing document for a Customer Success Manager.

## Graph Context
**Client Overview**: {json.dumps(ctx['overview'], default=str)}

**Deals**: 
{deal_info}

**Contacts** ({ctx['contacts'].get('count', 0)} total):
{json.dumps(ctx['contacts'].get('entities', [])[:5], default=str)}

**Risk Profile** ({ctx['risks'].get('risk_count', 0)} risks):
{json.dumps(ctx['risks'], default=str)}

**Products** ({ctx['products'].get('product_count', 0)} products):
{json.dumps(ctx['products'], default=str)}

**Success Metrics**: {json.dumps(ctx['success_metrics'].get('entities', []), default=str)}

**Commitments**: {json.dumps(ctx['commitments'].get('entities', []), default=str)}

**Objections**: {json.dumps(ctx['objections'].get('entities', []), default=str)}

## Instructions
Generate a professional briefing document in Markdown format for {csm_name}. Include:

1. **Executive Summary** — 2-3 sentences about the client and deal status
2. **Key Stakeholders** — Names, titles, roles, and engagement strategy for each
3. **Deal Overview** — Value, stage, products, timeline
4. **Risk Assessment** — Each risk with severity and derisking strategy
5. **Product Fit** — Products included, key features, known limitations to be aware of
6. **Success Metrics** — What the client expects to achieve
7. **Talking Points** — 3-5 specific items to discuss in the meeting
8. **Preparation Checklist** — Action items before the meeting

Keep it concise, actionable, and focused on what the CSM needs to know."""

    content = _generate(prompt, system="You are an expert Customer Success document generator. Output well-structured Markdown.")

    result = {
        "type": "briefing",
        "client_id": client_id,
        "title": f"Briefing Summary — {ctx['overview'].get('client_id', client_id)}",
        "content": content,
        "generated_at": datetime.utcnow().isoformat(),
        "metadata": {
            "risk_count": ctx["risks"].get("risk_count", 0),
            "product_count": ctx["products"].get("product_count", 0),
            "contact_count": ctx["contacts"].get("count", 0),
        },
    }

    # Persist to Firestore
    _save_output(client_id, result)
    return result


async def generate_action_plan(client_id: str, meeting_notes: str = None) -> dict:
    """Generate an action plan based on graph data and optional meeting notes.

    Args:
        client_id: Client identifier.
        meeting_notes: Optional notes from a recent meeting or session.

    Returns:
        Dict with structured action plan.
    """
    ctx = _collect_graph_context(client_id)

    notes_section = ""
    if meeting_notes:
        notes_section = f"\n## Meeting Notes\n{meeting_notes}\n"

    prompt = f"""You are generating a post-session action plan for a customer success team.

## Graph Context
**Client Overview**: {json.dumps(ctx['overview'], default=str)}
**Risks**: {json.dumps(ctx['risks'], default=str)}
**Commitments Made**: {json.dumps(ctx['commitments'].get('entities', []), default=str)}
**Objections Raised**: {json.dumps(ctx['objections'].get('entities', []), default=str)}
**Milestones**: {json.dumps(ctx['milestones'].get('entities', []), default=str)}
**Success Metrics**: {json.dumps(ctx['success_metrics'].get('entities', []), default=str)}
{notes_section}

## Instructions
Generate an action plan in Markdown. For each action item include:
- **Action**: Clear description
- **Owner**: Who should do it (CSM, client contact name, engineering)
- **Priority**: Critical / High / Medium / Low
- **Due**: Relative timeline (e.g., "Within 1 week", "Before next call")
- **Rationale**: Why this matters, linked to risks or commitments

Group actions by category:
1. **Immediate Follow-ups** — Next 48 hours
2. **This Week** — Within 5 business days
3. **This Month** — Before next QBR/milestone
4. **Ongoing Monitoring** — Recurring checks"""

    content = _generate(prompt, system="You are an expert project manager. Output actionable, prioritized plans in Markdown.")

    result = {
        "type": "action_plan",
        "client_id": client_id,
        "title": f"Action Plan — {client_id}",
        "content": content,
        "generated_at": datetime.utcnow().isoformat(),
        "metadata": {
            "has_meeting_notes": bool(meeting_notes),
        },
    }

    _save_output(client_id, result)
    return result


async def generate_risk_report(client_id: str) -> dict:
    """Generate a detailed risk assessment report.

    Args:
        client_id: Client identifier.

    Returns:
        Dict with risk report content.
    """
    risks = get_risk_profile(client_id)
    products = get_product_knowledge(client_id)

    prompt = f"""You are generating a comprehensive risk assessment report for executive review.

## Risk Data
{json.dumps(risks, default=str)}

## Product Context
{json.dumps(products, default=str)}

## Instructions
Generate a professional risk report in Markdown:

1. **Risk Summary Dashboard** — Table with: Risk, Category, Severity, Probability, Impact
2. **Critical Risks** — Detailed analysis of each critical/high risk with:
   - Root cause
   - Business impact if unmitigated
   - Recommended derisking strategy
   - Evidence supporting the assessment
3. **Product-Related Risks** — Risks linked to product limitations or features
4. **Trend Analysis** — Are risks increasing or decreasing?
5. **Recommendations** — Top 3 priorities for risk mitigation
6. **Escalation Criteria** — When should this be escalated to leadership"""

    content = _generate(prompt, system="You are a senior risk analyst. Output structured, evidence-based risk assessments in Markdown.")

    result = {
        "type": "risk_report",
        "client_id": client_id,
        "title": f"Risk Assessment — {client_id}",
        "content": content,
        "generated_at": datetime.utcnow().isoformat(),
        "metadata": {
            "severity_breakdown": risks.get("severity_breakdown", {}),
            "risk_count": risks.get("risk_count", 0),
        },
    }

    _save_output(client_id, result)
    return result


async def generate_recommendations(client_id: str, focus: str = "general") -> dict:
    """Generate strategic recommendations for a client engagement.

    Args:
        client_id: Client identifier.
        focus: Focus area — "general", "upsell", "retention", "expansion".

    Returns:
        Dict with recommendations content.
    """
    ctx = _collect_graph_context(client_id)

    prompt = f"""You are generating strategic recommendations for a customer success engagement.

## Focus: {focus}

## Graph Context
**Overview**: {json.dumps(ctx['overview'], default=str)}
**Products**: {json.dumps(ctx['products'], default=str)}
**Risks**: {json.dumps(ctx['risks'], default=str)}
**Success Metrics**: {json.dumps(ctx['success_metrics'].get('entities', []), default=str)}

## Instructions
Generate {focus}-focused recommendations in Markdown:

1. **Key Insights** — 3-5 data-driven insights from the knowledge graph
2. **Recommendations** — For each:
   - Recommendation title
   - Rationale (backed by graph data)
   - Expected impact
   - Implementation effort (Low/Medium/High)
   - Timeline
3. **Quick Wins** — Easy changes with high impact
4. **Strategic Moves** — Longer-term plays for account growth
5. **Risk Mitigations** — Recommendations to address current risks"""

    content = _generate(prompt, system="You are a strategic business advisor. Provide data-driven, actionable recommendations in Markdown.")

    result = {
        "type": "recommendations",
        "client_id": client_id,
        "title": f"Recommendations ({focus}) — {client_id}",
        "content": content,
        "generated_at": datetime.utcnow().isoformat(),
        "metadata": {"focus": focus},
    }

    _save_output(client_id, result)
    return result


async def generate_handoff(client_id: str, from_team: str, to_team: str) -> dict:
    """Generate a handoff document for transitioning a client between teams/stages.

    Args:
        client_id: Client identifier.
        from_team: Originating team (e.g., "Sales", "Onboarding").
        to_team: Receiving team (e.g., "Customer Success", "Support").

    Returns:
        Dict with handoff document content.
    """
    ctx = _collect_graph_context(client_id)

    prompt = f"""You are generating a handoff document for transitioning client ownership.

## Handoff: {from_team} → {to_team}

## Graph Context
**Overview**: {json.dumps(ctx['overview'], default=str)}
**Deals**: {json.dumps(ctx['deals'].get('entities', []), default=str)}
**Contacts**: {json.dumps(ctx['contacts'].get('entities', [])[:5], default=str)}
**Risks**: {json.dumps(ctx['risks'], default=str)}
**Products**: {json.dumps(ctx['products'], default=str)}
**Commitments**: {json.dumps(ctx['commitments'].get('entities', []), default=str)}

## Instructions
Generate a comprehensive handoff document in Markdown:

1. **Client Profile** — Company overview, industry, size, key contacts
2. **Deal Summary** — What was sold, value, timeline, expectations
3. **Relationship Map** — Key stakeholders and their roles/influence
4. **Commitments & Promises** — What was promised during {from_team} phase
5. **Known Risks** — Active risks with severity and mitigation status
6. **Product Configuration** — What's deployed, what's pending
7. **Open Items** — Unresolved issues or pending decisions
8. **Recommended First Steps** — What {to_team} should do first
9. **Critical Dates** — Renewal dates, milestones, review deadlines"""

    content = _generate(prompt, system=f"You are facilitating a smooth {from_team} to {to_team} transition. Output a thorough, well-organized handoff document in Markdown.")

    result = {
        "type": "handoff",
        "client_id": client_id,
        "title": f"Handoff: {from_team} → {to_team} — {client_id}",
        "content": content,
        "generated_at": datetime.utcnow().isoformat(),
        "metadata": {"from_team": from_team, "to_team": to_team},
    }

    _save_output(client_id, result)
    return result


# ── Persistence ───────────────────────────────────────────────────

def _save_output(client_id: str, output: dict):
    """Save a generated output to Firestore for retrieval by the Dashboard."""
    db = get_firestore_client()
    doc_id = f"{output['type']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    db.collection("knowledge_graphs").document(client_id).collection("outputs").document(doc_id).set({
        **output,
        "saved_at": datetime.utcnow().isoformat(),
    })

    print(f"[OUTPUTS] Saved {output['type']} for {client_id} as {doc_id}")


async def list_outputs(client_id: str) -> list[dict]:
    """List all generated outputs for a client.

    Args:
        client_id: Client identifier.

    Returns:
        List of output summaries (without full content to save bandwidth).
    """
    db = get_firestore_client()
    outputs_ref = (db.collection("knowledge_graphs")
                   .document(client_id)
                   .collection("outputs"))

    results = []
    for doc in outputs_ref.order_by("generated_at", direction="DESCENDING").stream():
        data = doc.to_dict()
        results.append({
            "id": doc.id,
            "type": data.get("type"),
            "title": data.get("title"),
            "generated_at": data.get("generated_at"),
            "metadata": data.get("metadata", {}),
        })

    return results


async def get_output(client_id: str, output_id: str) -> dict | None:
    """Retrieve a specific generated output by ID.

    Args:
        client_id: Client identifier.
        output_id: Output document ID.

    Returns:
        Full output dict including content, or None if not found.
    """
    db = get_firestore_client()
    doc = (db.collection("knowledge_graphs")
           .document(client_id)
           .collection("outputs")
           .document(output_id)
           .get())

    if not doc.exists:
        return None
    return doc.to_dict()
