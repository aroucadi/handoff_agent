"""Graph Generator — Ontology Schema.

Defines all node types, edge types, and their properties for the
Synapse knowledge graph.  This is the single source of truth that
drives entity extraction, graph storage, agent tool schemas, and
frontend visualization.

Layers:
  1. CRM Entities       — core deal/account/contact data
  2. Product Knowledge  — features, docs, limitations from Knowledge Center
  3. Deal Intelligence  — risks, derisking, metrics, objections, commitments
  4. Cross-Deal         — patterns, archetypes, playbooks (Phase 3)
  5. Agent Outputs      — briefings, action plans, recommendations (Phase 3)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


# ─── Node Type Definitions ────────────────────────────────────────

@dataclass(frozen=True)
class NodeType:
    """Schema for a knowledge graph node type."""
    name: str
    layer: str             # crm | product | intelligence | patterns | outputs
    description: str
    properties: dict[str, str]   # property_name → type hint (str, int, float, list[str], ...)
    icon: str = "●"         # for frontend visualization
    color: str = "#7b39fc"  # hex color for frontend


# Layer 1: CRM Entities
ORGANIZATION = NodeType(
    name="Organization",
    layer="crm",
    description="A company/account that is a customer or prospect",
    properties={
        "name": "str",
        "industry": "str",
        "size": "str",              # SMB, mid-market, enterprise
        "segment": "str",           # strategic, growth, velocity
        "hq_location": "str",
        "annual_revenue": "str",
        "employee_count": "int",
    },
    icon="🏢", color="#7b39fc",
)

DEAL = NodeType(
    name="Deal",
    layer="crm",
    description="A sales opportunity or active engagement being managed",
    properties={
        "deal_id": "str",
        "value": "float",
        "stage": "str",             # prospecting, negotiation, closed-won, etc.
        "close_date": "str",
        "win_probability": "float",
        "contract_length_months": "int",
        "products": "list[str]",
        "use_case": "str",
    },
    icon="💰", color="#7b39fc",
)

CONTACT = NodeType(
    name="Contact",
    layer="crm",
    description="A person involved in a deal or account relationship",
    properties={
        "name": "str",
        "title": "str",
        "role": "str",              # champion, blocker, decision-maker, influencer, end-user
        "influence_level": "str",   # high, medium, low
        "communication_style": "str",
        "email": "str",
        "department": "str",
    },
    icon="👤", color="#7b39fc",
)

ACTIVITY = NodeType(
    name="Activity",
    layer="crm",
    description="A recorded interaction such as a call, email, or meeting",
    properties={
        "type": "str",              # call, email, meeting, demo
        "date": "str",
        "summary": "str",
        "sentiment": "str",         # positive, neutral, negative
        "participants": "list[str]",
        "duration_minutes": "int",
    },
    icon="📅", color="#7b39fc",
)

CONTRACT = NodeType(
    name="Contract",
    layer="crm",
    description="A signed agreement governing a deal's terms",
    properties={
        "start_date": "str",
        "end_date": "str",
        "sla_go_live_days": "int",
        "support_tier": "str",      # premium, standard, basic
        "total_value": "str",
        "payment_terms": "str",
        "custom_clauses": "list[str]",
    },
    icon="📝", color="#7b39fc",
)

RENEWAL = NodeType(
    name="Renewal",
    layer="crm",
    description="An upcoming contract renewal event",
    properties={
        "renewal_date": "str",
        "likelihood": "str",        # high, medium, low
        "upsell_potential": "str",
        "churn_risk_score": "float",
        "notes": "str",
    },
    icon="🔄", color="#7b39fc",
)


# Layer 2: Product Knowledge
PRODUCT = NodeType(
    name="Product",
    layer="product",
    description="A software product offered by the platform",
    properties={
        "name": "str",
        "version": "str",
        "category": "str",          # portfolio-management, agile-planning, ppm, integration
        "tier": "str",              # standard, enterprise
        "target_segment": "str",
        "description": "str",
    },
    icon="📦", color="#10b981",
)

FEATURE = NodeType(
    name="Feature",
    layer="product",
    description="A specific capability or function within a product",
    properties={
        "name": "str",
        "description": "str",
        "maturity": "str",          # ga, beta, planned
        "scaling_notes": "str",
        "prerequisites": "list[str]",
    },
    icon="⚙️", color="#10b981",
)

USE_CASE = NodeType(
    name="UseCase",
    layer="product",
    description="A documented application scenario for a product or feature",
    properties={
        "title": "str",
        "industry_applicability": "list[str]",
        "prerequisites": "list[str]",
        "expected_outcomes": "str",
        "description": "str",
    },
    icon="🎯", color="#10b981",
)

KB_ARTICLE = NodeType(
    name="KBArticle",
    layer="product",
    description="A knowledge base article, guide, or best practice document",
    properties={
        "title": "str",
        "category": "str",          # guide, best-practice, release-notes, troubleshooting
        "url": "str",
        "summary": "str",
        "last_updated": "str",
    },
    icon="📄", color="#10b981",
)

LIMITATION = NodeType(
    name="Limitation",
    layer="product",
    description="A known constraint, scaling limit, or caveat of a product/feature",
    properties={
        "description": "str",
        "affected_feature": "str",
        "workaround": "str",
        "severity": "str",         # critical, moderate, minor
        "planned_fix_version": "str",
    },
    icon="⚠️", color="#f59e0b",
)

INTEGRATION = NodeType(
    name="Integration",
    layer="product",
    description="A connector or integration between the platform and an external system",
    properties={
        "partner_system": "str",    # Jira, Salesforce, SAP, etc.
        "sync_type": "str",         # bidirectional, unidirectional, event-driven
        "data_flow": "str",
        "rate_limits": "str",
        "authentication": "str",
    },
    icon="🔌", color="#10b981",
)


# Layer 3: Deal Intelligence
RISK = NodeType(
    name="Risk",
    layer="intelligence",
    description="A risk identified in a deal or implementation",
    properties={
        "category": "str",          # technical, political, timeline, resource, scope
        "description": "str",
        "severity": "str",          # critical, high, medium, low
        "probability": "str",       # high, medium, low
        "impact": "str",
        "owner": "str",
        "mitigation_deadline": "str",
    },
    icon="🔴", color="#ef4444",
)

DERISKING_STRATEGY = NodeType(
    name="DeriskingStrategy",
    layer="intelligence",
    description="A strategy or approach to mitigate an identified risk",
    properties={
        "risk_type": "str",
        "approach": "str",
        "evidence": "str",
        "success_rate": "str",
        "prerequisites": "list[str]",
        "recommended_timeline": "str",
    },
    icon="🛡️", color="#f97316",
)

SUCCESS_METRIC = NodeType(
    name="SuccessMetric",
    layer="intelligence",
    description="A measurable success criterion for a deal or implementation",
    properties={
        "name": "str",
        "baseline": "str",
        "target": "str",
        "measurement_method": "str",
        "timeline": "str",
        "owner": "str",
    },
    icon="📊", color="#10b981",
)

MILESTONE = NodeType(
    name="Milestone",
    layer="intelligence",
    description="A key date or deliverable in a deal's implementation plan",
    properties={
        "name": "str",
        "date": "str",
        "dependencies": "list[str]",
        "owner": "str",
        "status": "str",           # on-track, at-risk, missed, completed
        "blocker": "str",
    },
    icon="🏁", color="#3b82f6",
)

OBJECTION = NodeType(
    name="Objection",
    layer="intelligence",
    description="A concern or pushback raised by a stakeholder",
    properties={
        "topic": "str",
        "stakeholder": "str",
        "counter_argument": "str",
        "evidence": "str",
        "status": "str",           # open, addressed, escalated
    },
    icon="❌", color="#ef4444",
)

COMMITMENT = NodeType(
    name="Commitment",
    layer="intelligence",
    description="A promise or commitment made during a deal interaction",
    properties={
        "what": "str",
        "who": "str",
        "when": "str",
        "status": "str",           # pending, fulfilled, overdue, cancelled
        "source": "str",           # call on 2026-01-15, email from X
    },
    icon="🤝", color="#3b82f6",
)

COMPETITOR_MENTION = NodeType(
    name="CompetitorMention",
    layer="intelligence",
    description="A reference to a competitor during deal discussions",
    properties={
        "competitor_name": "str",
        "feature_compared": "str",
        "outcome": "str",          # we-won, they-won, ongoing
        "positioning_advice": "str",
    },
    icon="⚔️", color="#f59e0b",
)


# ─── Edge Type Definitions ────────────────────────────────────────

@dataclass(frozen=True)
class EdgeType:
    """Schema for a knowledge graph edge type."""
    name: str
    from_type: str
    to_type: str
    properties: dict[str, str] = field(default_factory=dict)
    description: str = ""


EDGE_TYPES: list[EdgeType] = [
    # CRM relationships
    EdgeType("HAS_DEAL", "Organization", "Deal",
             {"since": "str", "status": "str"},
             "An organization has an active deal"),
    EdgeType("EMPLOYS", "Organization", "Contact",
             {"since": "str", "active": "bool"},
             "An organization employs this contact"),
    EdgeType("CHAMPIONS", "Contact", "Deal",
             {"confidence": "str"},
             "A contact is championing this deal internally"),
    EdgeType("BLOCKS", "Contact", "Deal",
             {"reason": "str", "severity": "str"},
             "A contact is blocking or opposing this deal"),
    EdgeType("INFLUENCES", "Contact", "Deal",
             {"direction": "str"},
             "A contact has influence over this deal outcome"),
    EdgeType("PARTICIPATED_IN", "Contact", "Activity",
             {"role": "str"},
             "A contact participated in this activity"),
    EdgeType("GOVERNED_BY", "Deal", "Contract",
             {},
             "A deal is governed by this contract"),
    EdgeType("HAS_RENEWAL", "Deal", "Renewal",
             {},
             "A deal has an upcoming renewal"),

    # Product relationships
    EdgeType("INCLUDES", "Deal", "Product",
             {"quantity": "int", "config": "str"},
             "A deal includes this product"),
    EdgeType("HAS_FEATURE", "Product", "Feature",
             {},
             "A product provides this feature"),
    EdgeType("SOLVES", "Feature", "UseCase",
             {},
             "A feature addresses this use case"),
    EdgeType("HAS_LIMITATION", "Feature", "Limitation",
             {},
             "A feature has this known limitation"),
    EdgeType("DOCUMENTED_IN", "Product", "KBArticle",
             {},
             "A product is documented in this article"),
    EdgeType("INTEGRATES_WITH", "Product", "Integration",
             {},
             "A product integrates with this external system"),

    # Intelligence relationships
    EdgeType("HAS_RISK", "Deal", "Risk",
             {"identified_date": "str"},
             "A deal has this identified risk"),
    EdgeType("MITIGATED_BY", "Risk", "DeriskingStrategy",
             {},
             "A risk can be mitigated by this strategy"),
    EdgeType("EVIDENCED_BY", "DeriskingStrategy", "KBArticle",
             {},
             "A derisking strategy is evidenced by this article"),
    EdgeType("HAS_METRIC", "Deal", "SuccessMetric",
             {"priority": "str"},
             "A deal tracks this success metric"),
    EdgeType("HAS_MILESTONE", "Deal", "Milestone",
             {},
             "A deal has this implementation milestone"),
    EdgeType("RAISED", "Contact", "Objection",
             {"date": "str"},
             "A contact raised this objection"),
    EdgeType("COMMITTED_TO", "Contact", "Commitment",
             {"date": "str"},
             "A contact made this commitment"),
    EdgeType("MENTIONS_COMPETITOR", "Deal", "CompetitorMention",
             {},
             "A deal involves this competitor mention"),
    EdgeType("RELATED_TO", "KBArticle", "UseCase",
             {},
             "A KB article is related to this use case"),
]


# ─── Registry (lookup by name) ────────────────────────────────────

NODE_TYPES: dict[str, NodeType] = {nt.name: nt for nt in [
    ORGANIZATION, DEAL, CONTACT, ACTIVITY, CONTRACT, RENEWAL,
    PRODUCT, FEATURE, USE_CASE, KB_ARTICLE, LIMITATION, INTEGRATION,
    RISK, DERISKING_STRATEGY, SUCCESS_METRIC, MILESTONE,
    OBJECTION, COMMITMENT, COMPETITOR_MENTION,
]}

EDGE_TYPE_MAP: dict[str, EdgeType] = {et.name: et for et in EDGE_TYPES}


# ─── Extraction Prompt Helper ─────────────────────────────────────

def get_extraction_schema_prompt() -> str:
    """Generate the JSON schema instruction for Gemini entity extraction.

    Returns a prompt fragment describing valid node types, their properties,
    and valid edge types with from/to constraints.  Used by the rewritten
    node_generator to tell Gemini what to extract.
    """
    lines = ["## Valid Node Types\n"]
    for nt in NODE_TYPES.values():
        props = ", ".join(f'"{k}": {v}' for k, v in nt.properties.items())
        lines.append(f"- **{nt.name}** ({nt.layer}): {nt.description}")
        lines.append(f"  Properties: {{{props}}}\n")

    lines.append("\n## Valid Edge Types\n")
    for et in EDGE_TYPES:
        props = ", ".join(f'"{k}": {v}' for k, v in et.properties.items()) if et.properties else "none"
        lines.append(f"- **{et.name}**: {et.from_type} → {et.to_type} (props: {props})")
        lines.append(f"  {et.description}\n")

    return "\n".join(lines)
