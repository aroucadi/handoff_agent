"""Synapse Core Library — Normalization Utilities.

Unifies slugification and ID generation across Hub, Graph Generator, and Backend
to ensure "Zero Adaptation" consistency.
"""

import re

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
