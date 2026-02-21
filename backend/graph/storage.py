"""Handoff Backend — Graph Storage Module.

Reads skill graph nodes from GCS. Used by the ADK agent tools
for graph traversal during conversations.
"""

from __future__ import annotations

from google.cloud import storage as gcs

from config import config


def _get_client() -> gcs.Client:
    """Get GCS client."""
    return gcs.Client(project=config.project_id)


def read_node(client_id: str, node_id: str) -> str | None:
    """Read a client-specific node from GCS.

    Args:
        client_id: Client identifier.
        node_id: Node identifier (without .md extension).

    Returns:
        Markdown content or None if not found.
    """
    gcs_client = _get_client()
    bucket = gcs_client.bucket(config.skill_graphs_bucket)
    blob_path = f"clients/{client_id}/{node_id}.md"
    blob = bucket.blob(blob_path)

    if not blob.exists():
        return None

    return blob.download_as_text()


def read_static_node(path: str) -> str | None:
    """Read a static (product/industry) node from GCS.

    Args:
        path: Full path within the bucket, e.g. "product/cpq-module.md"
              or "industries/manufacturing/index.md"

    Returns:
        Markdown content or None if not found.
    """
    gcs_client = _get_client()
    bucket = gcs_client.bucket(config.skill_graphs_bucket)
    blob = bucket.blob(path)

    if not blob.exists():
        return None

    return blob.download_as_text()


def list_client_nodes(client_id: str) -> list[str]:
    """List all node IDs for a client.

    Returns:
        List of node_id strings.
    """
    gcs_client = _get_client()
    bucket = gcs_client.bucket(config.skill_graphs_bucket)
    prefix = f"clients/{client_id}/"
    blobs = bucket.list_blobs(prefix=prefix)

    node_ids = []
    for blob in blobs:
        name = blob.name.replace(prefix, "").replace(".md", "")
        if name:
            node_ids.append(name)
    return node_ids
