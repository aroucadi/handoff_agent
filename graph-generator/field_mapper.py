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
from core.normalization import apply_field_mapping, validate_mapping_result, _resolve_dot_path, _map_list_items

# field_mapper.py is now a legacy wrapper for core.normalization mapping logic
# maintaining it for backward compatibility with other modules if needed.
