"""Graph Generator — CRM Payload Entity Extractor.

Transforms the raw CRM webhook payload into structured graph entities
and relationships following the ontology schema.

Replaces the original flat-dict transform with typed entity extraction
that produces Organization, Deal, Contact, Risk, and SuccessMetric nodes
plus their connecting edges.
"""

from __future__ import annotations

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ontology import NODE_TYPES


def extract_entities_from_crm(payload: dict) -> dict:
    """Extract structured entities and relationships from a CRM webhook payload.

    Args:
        payload: Raw CRM webhook payload (already field-mapped by field_mapper.py).

    Returns:
        Dict with "nodes" (list of entity dicts) and "edges" (list of edge dicts).
        Each node has: {"id": str, "type": str, "properties": dict}
        Each edge has: {"type": str, "from_id": str, "to_id": str, "properties": dict}
    """
    tenant_id = payload.get("_tenant_id", "default")
    company_name = payload.get("company_name", "Unknown Company")
    raw_client_id = company_name.lower().replace(" ", "-").replace(",", "").replace(".", "")
    client_id = f"{tenant_id}_{raw_client_id}"

    nodes: list[dict] = []
    edges: list[dict] = []

    # ── Organization ────────────────────────────────────────
    org_id = f"{client_id}_org"
    nodes.append({
        "id": org_id,
        "type": "Organization",
        "properties": {
            "name": company_name,
            "industry": payload.get("industry", ""),
            "size": _classify_size(payload.get("employee_count", 0)),
            "segment": payload.get("segment", ""),
            "hq_location": payload.get("hq_location", ""),
            "annual_revenue": str(payload.get("annual_revenue", "")),
            "employee_count": payload.get("employee_count", 0),
        },
    })

    # ── Deal ────────────────────────────────────────────────
    deal_id_val = payload.get("deal_id", f"{client_id}_deal")
    deal_node_id = f"{client_id}_deal"
    products = payload.get("products", [])
    if isinstance(products, str):
        products = [p.strip() for p in products.split(",")]

    nodes.append({
        "id": deal_node_id,
        "type": "Deal",
        "properties": {
            "deal_id": deal_id_val,
            "value": payload.get("deal_value", 0),
            "stage": payload.get("stage", "closed-won"),
            "close_date": payload.get("close_date", ""),
            "win_probability": payload.get("win_probability", 1.0),
            "contract_length_months": payload.get("contract_length_months", 12),
            "products": products,
            "use_case": payload.get("use_case", ""),
        },
    })

    edges.append({
        "type": "HAS_DEAL",
        "from_id": org_id,
        "to_id": deal_node_id,
        "properties": {"status": "active"},
    })

    # ── Contacts ────────────────────────────────────────────
    contacts = payload.get("contacts", [])
    if isinstance(contacts, list):
        for i, contact in enumerate(contacts):
            if isinstance(contact, dict):
                c_name = contact.get("name", f"Contact {i+1}")
                c_id = f"{client_id}_contact_{i}"
                nodes.append({
                    "id": c_id,
                    "type": "Contact",
                    "properties": {
                        "name": c_name,
                        "title": contact.get("title", ""),
                        "role": contact.get("role", "stakeholder"),
                        "influence_level": contact.get("influence_level", "medium"),
                        "communication_style": contact.get("communication_style", ""),
                        "email": contact.get("email", ""),
                        "department": contact.get("department", ""),
                    },
                })

                # Org → Contact
                edges.append({
                    "type": "EMPLOYS",
                    "from_id": org_id,
                    "to_id": c_id,
                    "properties": {"active": True},
                })

                # Contact → Deal (role-based)
                role = contact.get("role", "").lower()
                if role in ("champion", "sponsor", "advocate"):
                    edges.append({
                        "type": "CHAMPIONS",
                        "from_id": c_id,
                        "to_id": deal_node_id,
                        "properties": {"confidence": contact.get("influence_level", "medium")},
                    })
                elif role in ("blocker", "detractor", "opponent"):
                    edges.append({
                        "type": "BLOCKS",
                        "from_id": c_id,
                        "to_id": deal_node_id,
                        "properties": {
                            "reason": contact.get("notes", ""),
                            "severity": contact.get("influence_level", "medium"),
                        },
                    })
                else:
                    edges.append({
                        "type": "INFLUENCES",
                        "from_id": c_id,
                        "to_id": deal_node_id,
                        "properties": {"direction": "neutral"},
                    })

    # ── Products (Deal → Product edges) ─────────────────────
    for j, product_name in enumerate(products):
        p_id = f"product_{product_name.lower().replace(' ', '-')}"
        # Don't create the Product node here — it comes from the Knowledge Center
        # Only create the edge linking the deal to the product
        edges.append({
            "type": "INCLUDES",
            "from_id": deal_node_id,
            "to_id": p_id,
            "properties": {"quantity": 1, "config": "standard"},
        })

    # ── Risks (extracted from payload if present) ───────────
    risks = payload.get("risks", [])
    if isinstance(risks, list):
        for k, risk in enumerate(risks):
            if isinstance(risk, dict):
                r_id = f"{client_id}_risk_{k}"
                nodes.append({
                    "id": r_id,
                    "type": "Risk",
                    "properties": {
                        "category": risk.get("category", "general"),
                        "description": risk.get("description", ""),
                        "severity": risk.get("severity", "medium"),
                        "probability": risk.get("probability", "medium"),
                        "impact": risk.get("impact", ""),
                        "owner": risk.get("owner", ""),
                        "mitigation_deadline": risk.get("deadline", ""),
                    },
                })
                edges.append({
                    "type": "HAS_RISK",
                    "from_id": deal_node_id,
                    "to_id": r_id,
                    "properties": {},
                })

    # ── Success Metrics ─────────────────────────────────────
    metrics = payload.get("success_metrics", [])
    if isinstance(metrics, list):
        for m, metric in enumerate(metrics):
            if isinstance(metric, dict):
                m_id = f"{client_id}_metric_{m}"
                nodes.append({
                    "id": m_id,
                    "type": "SuccessMetric",
                    "properties": {
                        "name": metric.get("name") or metric.get("metric", ""),
                        "baseline": metric.get("baseline") or metric.get("current_value", ""),
                        "target": metric.get("target") or metric.get("target_value", ""),
                        "measurement_method": metric.get("method", ""),
                        "timeline": metric.get("timeline") or metric.get("timeframe", ""),
                        "owner": metric.get("owner", ""),
                    },
                })
                edges.append({
                    "type": "HAS_METRIC",
                    "from_id": deal_node_id,
                    "to_id": m_id,
                    "properties": {"priority": metric.get("priority", "medium")},
                })

    return {
        "nodes": nodes,
        "edges": edges,
        "client_id": client_id,
        "tenant_id": tenant_id,
    }


# ── Legacy compatibility ────────────────────────────────────────

def extract_from_crm_payload(payload: dict) -> dict:
    """Legacy API — returns flat dict for backward compatibility with the
    old node_generator prompt.  Will be removed once migration is complete.
    """
    return {
        "company_name": payload.get("company_name", "Unknown"),
        "industry": payload.get("industry", "general"),
        "deal_value": payload.get("deal_value", 0),
        "products": payload.get("products", []),
        "contacts": payload.get("contacts", []),
        "pain_points": payload.get("pain_points", []),
        "close_date": payload.get("close_date", "TBD"),
        "stage": payload.get("stage", "closed-won"),
        "csm_id": payload.get("csm_id", ""),
        "deal_id": payload.get("deal_id", ""),
    }


def _classify_size(employee_count: int) -> str:
    """Classify organization size from employee count."""
    if employee_count <= 0:
        return "unknown"
    elif employee_count < 200:
        return "SMB"
    elif employee_count < 2000:
        return "mid-market"
    else:
        return "enterprise"
