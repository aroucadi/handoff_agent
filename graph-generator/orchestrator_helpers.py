"""Graph Generator — Orchestrator Helpers.

Contains logic for merging tenant knowledge into CRM entities.
"""

from __future__ import annotations
import os
import sys

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import config
from core.db import get_firestore_client

def extract_product_ids_from_crm_entities(crm_entities: dict) -> set[str]:
    product_ids: set[str] = set()
    for edge in crm_entities.get("edges", []) or []:
        if edge.get("type") == "INCLUDES":
            to_id = edge.get("to_id", "")
            if isinstance(to_id, str) and to_id.startswith("product_"):
                product_ids.add(to_id)
    return product_ids


def load_tenant_knowledge(tenant_id: str) -> tuple[dict[str, dict], list[dict]]:
    db = get_firestore_client()
    root = db.collection("tenant_knowledge").document(tenant_id)
    entities: dict[str, dict] = {}
    for doc in root.collection("entities").stream():
        entities[doc.id] = doc.to_dict()

    edges: list[dict] = []
    for doc in root.collection("edges").stream():
        edges.append(doc.to_dict())

    return entities, edges


def select_subgraph(entities: dict[str, dict], edges: list[dict], seed_ids: set[str], max_hops: int = 2) -> tuple[list[dict], list[dict]]:
    adjacency: dict[str, list[dict]] = {}
    for edge in edges:
        src = edge.get("from_id", "")
        dst = edge.get("to_id", "")
        if isinstance(src, str) and isinstance(dst, str) and src and dst:
            adjacency.setdefault(src, []).append(edge)

    visited: set[str] = set()
    frontier = list(seed_ids)
    selected_edges: list[dict] = []

    for _ in range(max_hops):
        next_frontier: list[str] = []
        for current in frontier:
            if current in visited:
                continue
            visited.add(current)
            for edge in adjacency.get(current, []):
                selected_edges.append({
                    "type": edge.get("type", "RELATED_TO"),
                    "from_id": edge.get("from_id", ""),
                    "to_id": edge.get("to_id", ""),
                    "properties": edge.get("properties", {}) or {},
                })
                nxt = edge.get("to_id", "")
                if isinstance(nxt, str) and nxt and nxt not in visited:
                    next_frontier.append(nxt)
        frontier = next_frontier

    selected_nodes: list[dict] = []
    for entity_id in visited:
        ent = entities.get(entity_id)
        if not ent:
            continue
        selected_nodes.append({
            "id": ent.get("entity_id", entity_id),
            "type": ent.get("type", "Unknown"),
            "properties": ent.get("properties", {}) or {},
        })

    return selected_nodes, selected_edges


def merge_tenant_knowledge_into_crm_entities(crm_entities: dict, tenant_id: str) -> dict:
    product_ids = extract_product_ids_from_crm_entities(crm_entities)
    if not tenant_id or not product_ids:
        return crm_entities

    entities, edges = load_tenant_knowledge(tenant_id)
    if not entities:
        return crm_entities

    selected_nodes, selected_edges = select_subgraph(entities, edges, product_ids, max_hops=2)

    existing_ids = {n.get("id") for n in crm_entities.get("nodes", []) or []}
    for node in selected_nodes:
        node_id = node.get("id")
        if node_id and node_id not in existing_ids:
            crm_entities.setdefault("nodes", []).append(node)
            existing_ids.add(node_id)

    crm_entities.setdefault("edges", []).extend(selected_edges)
    return crm_entities
