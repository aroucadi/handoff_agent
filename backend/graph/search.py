"""Handoff Backend — Graph Search Module.

Provides vector search over skill graph nodes using embeddings stored in Firestore.
Uses gemini-embedding-001 for query embedding.
"""

from __future__ import annotations

from google import genai
from google.genai.types import EmbedContentConfig
from google.cloud import firestore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector

from core.config import config


def _get_firestore() -> firestore.Client:
    """Get Firestore client."""
    from core.db import get_firestore_client
    return get_firestore_client()


def embed_query(query: str) -> list[float]:
    """Generate embedding for a search query using gemini-embedding-001."""
    client = genai.Client(api_key=config.gemini_api_key)

    result = client.models.embed_content(
        model=config.embedding_model,
        contents=query,
        config=EmbedContentConfig(
            output_dimensionality=config.embedding_dims,
        ),
    )

    return result.embeddings[0].values


def search_nodes(client_id: str, query: str, top_k: int = 5) -> list[dict]:
    """Search for relevant nodes using vector similarity.

    Args:
        client_id: Client to search within.
        query: Natural language search query.
        top_k: Number of results to return.

    Returns:
        List of matching node summaries with similarity scores.
    """
    query_embedding = embed_query(query)

    db = _get_firestore()
    nodes_ref = db.collection("skill_graphs").document(client_id).collection("nodes")
    
    # Use Firestore Native Vector Search (FindNearest)
    # This prevents loading every node into memory for manual cosine similarity
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
            # Note: With find_nearest, distance isn't automatically injected into
            # the doc dict by the Python SDK, but returning the ranked list is sufficient.
        })

    return results
