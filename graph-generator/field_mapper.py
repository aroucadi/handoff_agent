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


def _map_list_items(value: Any, item_map: dict[str, str], preserve_unmapped: bool) -> Any:
    if not isinstance(value, list):
        return value
    mapped_list: list[Any] = []
    for item in value:
        if not isinstance(item, dict):
            mapped_list.append(item)
            continue
        out: dict[str, Any] = {}
        for src_key, dst_key in item_map.items():
            if src_key in item and item[src_key] is not None:
                out[dst_key] = item[src_key]
        if preserve_unmapped:
            for k, v in item.items():
                if k not in item_map and k not in out:
                    out[k] = v
        mapped_list.append(out)
    return mapped_list


def apply_field_mapping(raw_payload: dict, mapping: dict[str, Any]) -> dict:
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

    for source_path, target_spec in mapping.items():
        value = _resolve_dot_path(raw_payload, source_path)
        if value is None:
            continue

        if isinstance(target_spec, str):
            normalized[target_spec] = value
            mapped_source_keys.add(source_path.split(".")[0])
            continue

        if isinstance(target_spec, dict):
            target_field = target_spec.get("target")
            if not target_field:
                continue
            item_map = target_spec.get("item_map")
            preserve_unmapped = bool(target_spec.get("preserve_unmapped", True))
            if item_map and isinstance(item_map, dict):
                normalized[target_field] = _map_list_items(value, item_map, preserve_unmapped)
            else:
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
