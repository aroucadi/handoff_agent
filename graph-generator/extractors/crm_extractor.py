"""Graph Generator — CRM Data Extractor.

Structures the raw CRM webhook payload into a format suitable for graph generation.
No Gemini call needed — this is straightforward data transformation.
"""

from __future__ import annotations


def extract_from_crm_payload(payload: dict) -> dict:
    """Extract structured entities from the CRM webhook payload.

    Args:
        payload: Raw webhook JSON from CRM Simulator.

    Returns:
        Dictionary with CRM-sourced entities for graph generation.
    """
    return {
        "company": {
            "name": payload.get("company_name", "Unknown"),
            "industry": payload.get("industry", ""),
            "employee_count": payload.get("employee_count"),
        },
        "deal": {
            "deal_id": payload.get("deal_id", ""),
            "value": payload.get("deal_value", 0),
            "close_date": payload.get("close_date", ""),
            "sla_days": payload.get("sla_days"),
            "products": payload.get("products", []),
        },
        "contacts": payload.get("contacts", []),
        "risks": payload.get("risks", []),
        "success_metrics": payload.get("success_metrics", []),
        "csm_id": payload.get("csm_id"),
    }
