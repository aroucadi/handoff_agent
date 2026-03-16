"""
Graph Generator — Dynamic Field Mapping Engine

Translates incoming CRM webhook payloads into Synapse's internal schema
using per-tenant field mappings stored in Firestore.

Supports:
- Flat field mapping: "Amount" → "deal_value"
- Dot-notation for nested fields: "sobject.Name" → payload["sobject"]["Name"]
- Array passthrough: fields that resolve to lists are passed through as-is
"""

from __future__ import annotations

from typing import Any


def _resolve_dot_path(obj: dict, path: str) -> Any:
    """Resolve a dot-notation path against a nested dict.

    Examples:
        _resolve_dot_path({"a": {"b": 1}}, "a.b") → 1
        _resolve_dot_path({"x": 5}, "x") → 5
        _resolve_dot_path({"a": 1}, "a.b.c") → None
    """
    parts = path.split(".")
    current = obj
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
        if current is None:
            return None
    return current


def apply_field_mapping(raw_payload: dict, mapping: dict[str, str]) -> dict:
    """Transform an incoming CRM payload using a field mapping dict.

    Args:
        raw_payload: The raw JSON payload from the CRM webhook.
        mapping: Dict mapping CRM field paths → Synapse internal field names.
                 Example: {"sobject.Name": "company_name", "Amount": "deal_value"}

    Returns:
        A normalized payload using Synapse's internal field names.
        Unmapped fields from the raw payload are preserved under "_unmapped".
    """
    normalized = {}
    mapped_source_keys = set()

    for source_path, target_field in mapping.items():
        value = _resolve_dot_path(raw_payload, source_path)
        if value is not None:
            normalized[target_field] = value
            # Track top-level key as mapped
            mapped_source_keys.add(source_path.split(".")[0])

    # Preserve unmapped top-level fields (useful for debugging and extensibility)
    unmapped = {}
    for key, value in raw_payload.items():
        if key not in mapped_source_keys and not key.startswith("_"):
            unmapped[key] = value

    if unmapped:
        normalized["_unmapped"] = unmapped

    # Preserve any Synapse metadata fields that start with "_"
    for key, value in raw_payload.items():
        if key.startswith("_"):
            normalized[key] = value

    return normalized


def validate_mapping_result(normalized: dict) -> list[str]:
    """Check if a normalized payload has the minimum required fields.

    Returns:
        List of missing required field names. Empty list means valid.
    """
    required_fields = ["deal_id", "company_name"]
    recommended_fields = ["deal_value", "close_date", "industry"]

    missing = []
    for field in required_fields:
        if not normalized.get(field):
            missing.append(f"REQUIRED: {field}")
    for field in recommended_fields:
        if not normalized.get(field):
            missing.append(f"RECOMMENDED: {field}")

    return missing
