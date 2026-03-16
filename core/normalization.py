"""Synapse Core Library — Normalization Utilities.

Unifies slugification and ID generation across Hub, Graph Generator, and Backend
to ensure "Zero Adaptation" consistency.
"""

import re
from typing import Any

def slugify(name: str) -> str:
    """Convert a string to a kebab-case slug."""
    if not name:
        return "unknown"
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "unknown"

def generate_product_id(name: str) -> str:
    """Standardize product ID generation."""
    return f"product_{slugify(name)}"

def generate_client_id(tenant_id: str, company_name: str) -> str:
    """Standardize client ID generation."""
    return f"{tenant_id}_{slugify(company_name)}"

def normalize_stage(raw_stage: str, stage_mapping: dict | None = None) -> str:
    """Normalize a CRM stage to a canonical Synapse stage."""
    if not raw_stage:
        return "unknown"
    
    if not stage_mapping:
        return raw_stage
        
    # Direct match
    if raw_stage in stage_mapping:
        return stage_mapping[raw_stage]
        
    # Case-insensitive match
    stage_map_lower = {k.lower(): v for k, v in stage_mapping.items()}
    return stage_map_lower.get(raw_stage.lower(), raw_stage)

def normalize_product_id(product_name: str, product_alias_map: dict | None = None) -> str:
    """Normalize a CRM product name to a canonical product ID."""
    if not product_name:
        return "unknown"
        
    if product_alias_map:
        if product_name in product_alias_map:
            return product_alias_map[product_name]
        
        # Case-insensitive fallback
        alias_map_lower = {k.lower(): v for k, v in product_alias_map.items()}
        if product_name.lower() in alias_map_lower:
            return alias_map_lower[product_name.lower()]
            
    return generate_product_id(product_name)

def _resolve_dot_path(obj: dict, path: str) -> Any:
    """Resolve a dot-notation path against a nested dict."""
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
    """Transform an incoming CRM payload using a field mapping dict."""
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
            mapped_source_keys.add(source_path.split(".")[0])

    # Preserve unmapped top-level fields
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
    """Check if a normalized payload has the minimum required fields."""
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
