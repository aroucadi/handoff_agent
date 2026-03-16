"""Synapse Backend — Graph Search Module.

Provides vector search over skill graph nodes using embeddings in Firestore.
Supports both legacy `skill_graphs/` and structured `knowledge_graphs/` collections.
"""

from __future__ import annotations

from google import genai
from google.genai.types import EmbedContentConfig
from google.cloud.firestore_v1.vector import Vector

from core.config import config
from core.auth import verify_tenant_access


def _get_firestore() -> firestore.Client:
    """Get Firestore client."""
    from core.db import get_firestore_client
    return get_firestore_client()


def embed_query(query: str) -> list[float]:
    """Generate embedding for a search query using gemini-embedding-001."""
    client = genai.Client(vertexai=True, project=config.project_id, location=config.region)

    result = client.models.embed_content(
        model=config.embedding_model,
        contents=query,
        config=EmbedContentConfig(
            output_dimensionality=config.embedding_dims,
        ),
    )

    return result.embeddings[0].values


# ── Legacy Search (skill_graphs) ─────────────────────────────────

def search_nodes(tenant_id: str, client_id: str, query: str, top_k: int = 5) -> list[dict]:
    """Search for relevant nodes using vector similarity (legacy markdown graphs).

    Args:
        tenant_id: The tenant identifier
        client_id: Client to search within.
        query: Natural language search query.
        top_k: Number of results to return.

    Returns:
        List of matching node summaries with similarity scores.
    """
    _verify_tenant_access(tenant_id, client_id)
    query_embedding = embed_query(query)

    db = _get_firestore()
    nodes_ref = db.collection("skill_graphs").document(client_id).collection("nodes")
    
    docs = nodes_ref.find_nearest(
        vector_field="embedding",
        query_vector=Vector(query_embedding),
        distance_measure=DistanceMeasure.COSINE,
        limit=top_k,
    ).stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append({
            "node_id": data.get("node_id"),
            "title": data.get("title"),
            "description": data.get("description"),
            "body_preview": data.get("body_preview", "")[:200],
        })

    return results


# ── Structured Entity Search (knowledge_graphs) ──────────────────

def search_entities(
    tenant_id: str,
    client_id: str,
    query: str,
    entity_type: str = None,
    top_k: int = 5,
) -> list[dict]:
    """Semantic search over structured knowledge graph entities.

    Uses Firestore vector search (find_nearest) on the `knowledge_graphs/`
    collection. Optionally filters by entity type.

    Args:
        tenant_id: The tenant identifier
        client_id: Client to search within.
        query: Natural language search query.
        entity_type: Optional entity type filter (e.g. "Risk", "Feature").
        top_k: Number of results to return.

    Returns:
        List of matching entities with their types and properties.
    """
    _verify_tenant_access(tenant_id, client_id)
    query_embedding = embed_query(query)

    db = _get_firestore()
    entities_ref = (db.collection("knowledge_graphs")
                    .document(client_id)
                    .collection("entities"))

    # Apply type filter if specified
    if entity_type:
        entities_ref = entities_ref.where("type", "==", entity_type)

    try:
        docs = entities_ref.find_nearest(
            vector_field="embedding",
            query_vector=Vector(query_embedding),
            distance_measure=DistanceMeasure.COSINE,
            limit=top_k,
        ).stream()
    except Exception as e:
        # Fallback: manual cosine similarity if find_nearest fails
        # (e.g., no vector index configured)
        print(f"[SEARCH] find_nearest failed, falling back to manual search: {e}")
        return _manual_vector_search(entities_ref, query_embedding, entity_type, top_k)

    results = []
    for doc in docs:
        data = doc.to_dict()
        data.pop("embedding", None)
        data.pop("indexed_at", None)
        results.append(data)

    return results


def _manual_vector_search(
    entities_ref,
    query_embedding: list[float],
    entity_type: str = None,
    top_k: int = 5,
) -> list[dict]:
    """Fallback: manual cosine similarity search when vector index is unavailable."""
    results = []

    for doc in entities_ref.stream():
        data = doc.to_dict()

        if entity_type and data.get("type") != entity_type:
            continue

        stored_embedding = data.get("embedding", [])
        if not stored_embedding:
            continue

        # Cosine similarity
        dot = sum(a * b for a, b in zip(query_embedding, stored_embedding))
        norm_a = sum(a * a for a in query_embedding) ** 0.5
        norm_b = sum(b * b for b in stored_embedding) ** 0.5
        similarity = dot / (norm_a * norm_b) if norm_a and norm_b else 0

        data.pop("embedding", None)
        data.pop("indexed_at", None)
        data["similarity"] = round(similarity, 4)
        results.append(data)

    results.sort(key=lambda r: r.get("similarity", 0), reverse=True)
    return results[:top_k]
