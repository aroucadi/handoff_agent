"""Synapse Backend — Agent Generative Outputs.

Produces structured documents from the knowledge graph using Gemini:
  - Briefing summaries
  - Action plans
  - Risk reports
  - Recommendations
  - Handoff documents
  - Role-based transcripts / scripts (sales, support, QBR, renewal, etc.)
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


# ── Role-Based Transcript / Script Generator ─────────────────────

# Supported transcript types with their system personas and structure
TRANSCRIPT_TYPES = {
    "sales_script": {
        "title": "Sales Call Script",
        "system": "You are an expert sales coach who crafts compelling, natural-sounding call scripts. You focus on value-based selling, consultative approaches, and handling objections with confidence.",
        "structure": [
            "Opening & Rapport Building — Personalized opener referencing the client's industry/company",
            "Discovery Questions — 3-5 targeted questions based on known gaps or opportunities",
            "Value Proposition — Tailored pitch connecting products to client's specific needs",
            "Objection Handling — Pre-built responses to each known objection from the graph",
            "Competitive Positioning — How to handle competitor mentions",
            "Pricing Discussion — Anchoring and negotiation tactics",
            "Next Steps & Close — Clear call-to-action and commitment request",
        ],
    },
    "support_script": {
        "title": "Customer Support Script",
        "system": "You are an experienced customer support specialist who excels at de-escalation and empathy-driven problem resolution. You help agents handle frustrated customers with patience and professionalism.",
        "structure": [
            "Greeting & Acknowledgment — Empathetic opening acknowledging their frustration",
            "Active Listening Prompts — Questions to understand the root issue",
            "Known Issues — Script for each risk/limitation from the knowledge graph",
            "De-escalation Techniques — Specific language to calm frustrated customers",
            "Resolution Paths — Step-by-step solutions for common problems",
            "Escalation Protocol — When and how to escalate, with warm handoff language",
            "Follow-up Commitment — Specific promises to make and keep",
        ],
    },
    "qbr_prep": {
        "title": "QBR Discussion Guide",
        "system": "You are a strategic Customer Success Manager preparing for an executive-level Quarterly Business Review. You create structured agendas that demonstrate value and drive strategic alignment.",
        "structure": [
            "Welcome & Agenda Setting — Professional opener with clear meeting goals",
            "Value Delivered Summary — ROI metrics and wins since last QBR",
            "Adoption Metrics Discussion — Usage data, active users, feature adoption",
            "Success Metric Review — Progress against each defined success metric",
            "Risk Discussion — Transparent discussion of challenges and derisking plans",
            "Product Roadmap Preview — Upcoming features relevant to this client",
            "Strategic Alignment — Ensuring product direction matches client goals",
            "Next Quarter Goals — Specific, measurable targets to agree on",
        ],
    },
    "renewal_script": {
        "title": "Renewal Conversation Script",
        "system": "You are a skilled renewal specialist who builds strong cases for contract renewal and expansion. You focus on demonstrated value, risk mitigation, and mutual growth.",
        "structure": [
            "Opening — Re-establish relationship and set a positive tone",
            "Value Recap — Specific outcomes achieved with data points",
            "ROI Summary — Cost vs. value delivered, with concrete examples",
            "Risk of Churning — Address known risks and competitor mentions proactively",
            "Expansion Opportunity — Natural upsell based on product fit analysis",
            "Contract Terms Discussion — Pricing, term length, SLA adjustments",
            "Objection Handling — Responses to budget, timing, and competitor objections",
            "Close & Next Steps — Clear commitment ask with timeline",
        ],
    },
    "onboarding_guide": {
        "title": "Onboarding Walkthrough Script",
        "system": "You are an onboarding specialist who creates structured, easy-to-follow guides that help new customers get value quickly. You focus on quick wins and building confidence.",
        "structure": [
            "Welcome & Introduction — Warm welcome with overview of what to expect",
            "Account Setup — Step-by-step initial configuration based on products purchased",
            "Key Feature Tour — Guided walkthrough of the features most relevant to their use cases",
            "Quick Win Exercise — A hands-on activity that demonstrates immediate value",
            "Known Limitations — Transparent discussion of limitations with workarounds",
            "Integration Setup — How to connect with their existing tools",
            "Training Resources — Links to relevant KB articles and guides",
            "30-60-90 Day Plan — Clear milestones for the first 90 days",
        ],
    },
    "discovery_questions": {
        "title": "Discovery & Qualification Questions",
        "system": "You are a consultative sales expert who crafts probing discovery questions that uncover needs, pain points, and buying signals. You help sellers go beyond surface-level conversations.",
        "structure": [
            "Company & Context — Questions about their current situation and why they're looking",
            "Pain Points — Deep-dive questions into specific challenges based on graph data",
            "Decision Process — Who's involved, timeline, budget, and authority mapping",
            "Current Solutions — What they use today, what's working, what's not",
            "Success Criteria — How they'll measure success with specific metrics",
            "Objection Surfacing — Questions that proactively uncover potential blockers",
            "Competitive Landscape — Questions to understand alternatives being considered",
            "Next Steps — Qualification checklist and recommended follow-up actions",
        ],
    },
}


async def generate_transcript(
    client_id: str,
    transcript_type: str = "sales_script",
    user_role: str = None,
    additional_context: str = None,
) -> dict:
    """Generate a role-based transcript or script from the knowledge graph.

    Produces a contextual, ready-to-use script tailored to a specific role
    and scenario. The script leverages knowledge graph data (risks, contacts,
    objections, products) to create personalized, data-driven talking points.

    Args:
        client_id: Client identifier.
        transcript_type: Type of transcript. Options:
            "sales_script", "support_script", "qbr_prep",
            "renewal_script", "onboarding_guide", "discovery_questions"
        user_role: Optional role of the person using the script (e.g., "AE", "CSM").
        additional_context: Optional extra context (e.g., session notes, CRM comments).

    Returns:
        Dict with title, content (markdown), and metadata.
    """
    ttype = TRANSCRIPT_TYPES.get(transcript_type)
    if not ttype:
        available = ", ".join(TRANSCRIPT_TYPES.keys())
        return {"error": f"Unknown transcript type '{transcript_type}'. Available: {available}"}

    ctx = _collect_graph_context(client_id)

    # Build role context
    role_line = f"for a {user_role}" if user_role else ""
    extra_section = ""
    if additional_context:
        extra_section = f"\n## Additional Context from User\n{additional_context}\n"

    structure_text = "\n".join(f"{i+1}. **{item}**" for i, item in enumerate(ttype["structure"]))

    prompt = f"""Generate a "{ttype['title']}" {role_line} for the following client engagement.

## Client Knowledge Graph
**Overview**: {json.dumps(ctx['overview'], default=str)}

**Key Contacts** ({ctx['contacts'].get('count', 0)} total):
{json.dumps(ctx['contacts'].get('entities', [])[:5], default=str)}

**Products**: {json.dumps(ctx['products'], default=str)}

**Risk Profile** ({ctx['risks'].get('risk_count', 0)} risks):
{json.dumps(ctx['risks'], default=str)}

**Objections Raised**: {json.dumps(ctx['objections'].get('entities', []), default=str)}

**Commitments Made**: {json.dumps(ctx['commitments'].get('entities', []), default=str)}

**Success Metrics**: {json.dumps(ctx['success_metrics'].get('entities', []), default=str)}

**Competitor Mentions**: {json.dumps(get_entities_by_type(client_id, 'CompetitorMention').get('entities', []), default=str)}
{extra_section}

## Required Structure
{structure_text}

## Instructions
- Write in a **conversational, natural tone** — this should sound like a real person talking, not a template.
- Include **specific names, numbers, and details** from the graph data whenever possible.
- For each section, provide the actual words/sentences the person should say or ask.
- Mark key decision points with [IF...THEN] branching where the conversation could go different ways.
- Highlight **danger zones** where the script user should be extra careful (e.g., known objections, frustrated contacts).
- End with a clear set of commitments to secure from the customer.

Output as well-structured Markdown with clear section headers."""

    content = _generate(prompt, system=ttype["system"])

    result = {
        "type": "transcript",
        "subtype": transcript_type,
        "client_id": client_id,
        "title": f"{ttype['title']} — {client_id}",
        "content": content,
        "generated_at": datetime.utcnow().isoformat(),
        "metadata": {
            "transcript_type": transcript_type,
            "user_role": user_role,
            "has_additional_context": bool(additional_context),
            "risk_count": ctx["risks"].get("risk_count", 0),
            "contact_count": ctx["contacts"].get("count", 0),
        },
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
