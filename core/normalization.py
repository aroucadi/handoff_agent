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
