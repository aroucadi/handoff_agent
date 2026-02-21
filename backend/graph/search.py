"""Handoff Backend — Graph Search Module.

Provides vector search over skill graph nodes using embeddings stored in Firestore.
Uses gemini-embedding-001 for query embedding.
"""

from __future__ import annotations

from google import genai
from google.genai.types import EmbedContentConfig
from google.cloud import firestore

from config import config


def _get_firestore() -> firestore.Client:
    """Get Firestore client."""
    return firestore.Client(project=config.project_id)


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
    docs = nodes_ref.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        stored_embedding = data.get("embedding", [])
        if not stored_embedding:
            continue

        # Cosine similarity
        dot = sum(a * b for a, b in zip(query_embedding, stored_embedding))
        norm_a = sum(a * a for a in query_embedding) ** 0.5
        norm_b = sum(b * b for b in stored_embedding) ** 0.5
        similarity = dot / (norm_a * norm_b) if norm_a and norm_b else 0

        results.append({
            "node_id": data.get("node_id"),
            "title": data.get("title"),
            "description": data.get("description"),
            "similarity": round(similarity, 4),
            "body_preview": data.get("body_preview", "")[:200],
        })

    results.sort(key=lambda r: r["similarity"], reverse=True)
    return results[:top_k]
