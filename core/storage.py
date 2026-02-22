"""Synapse Core Library — Google Cloud Storage Singleton.

Provides a unified, reusable GCS client to prevent repeated
inline instantiations and abstract common bucket operations
shared by the backend and graph-generator services.
"""

from typing import Optional
from google.cloud import storage as gcs

from core.config import config


# Global singleton instance
_gcs_client: Optional[gcs.Client] = None


def get_gcs_client() -> gcs.Client:
    """Get or create the Google Cloud Storage client singleton."""
    global _gcs_client
    if _gcs_client is None:
        _gcs_client = gcs.Client(project=config.project_id)
    return _gcs_client


async def write_node_to_gcs(client_id: str, node_id: str, content: str) -> str:
    """Write a single markdown node file to GCS.

    Args:
        client_id: Client identifier for the path prefix.
        node_id: Node identifier (used as filename).
        content: Full markdown content including YAML frontmatter.

    Returns:
        GCS URI of the written file.
    """
    gcs_client = get_gcs_client()
    bucket = gcs_client.bucket(config.skill_graphs_bucket)

    blob_path = f"clients/{client_id}/{node_id}.md"
    blob = bucket.blob(blob_path)
    # GCS sync operations within an async context are acceptable
    # for this scale, but could be offloaded to threadpool if needed.
    blob.upload_from_string(content, content_type="text/markdown")

    uri = f"gs://{config.skill_graphs_bucket}/{blob_path}"
    print(f"[GCS] Written: {uri}")
    return uri


async def write_all_nodes(client_id: str, nodes: list[dict]) -> list[str]:
    """Write all generated nodes to GCS.

    Args:
        client_id: Client identifier.
        nodes: List of dicts with "node_id" and "content".

    Returns:
        List of GCS URIs.
    """
    uris = []
    for node in nodes:
        node_id = node.get("node_id", "unknown")
        content = node.get("content", "")
        uri = await write_node_to_gcs(client_id, node_id, content)
        uris.append(uri)
    return uris


def read_node(client_id: str, node_id: str) -> str | None:
    """Read a client-specific node from GCS."""
    gcs_client = get_gcs_client()
    bucket = gcs_client.bucket(config.skill_graphs_bucket)
    blob_path = f"clients/{client_id}/{node_id}.md"
    blob = bucket.blob(blob_path)

    if not blob.exists():
        # Fallback for paths requested without extension
        return None

    return blob.download_as_text()


def read_static_node(path: str) -> str | None:
    """Read a static (product/industry) node from GCS.

    Args:
        path: Full path within the bucket, e.g. "product/index.md"
    """
    gcs_client = get_gcs_client()
    bucket = gcs_client.bucket(config.skill_graphs_bucket)
    blob = bucket.blob(path)

    if not blob.exists():
        return None

    return blob.download_as_text()


def list_client_nodes(client_id: str) -> list[str]:
    """List all node IDs for a client.

    Returns:
        List of node_id strings (without .md extension).
    """
    gcs_client = get_gcs_client()
    bucket = gcs_client.bucket(config.skill_graphs_bucket)
    prefix = f"clients/{client_id}/"
    blobs = bucket.list_blobs(prefix=prefix)

    node_ids = []
    for blob in blobs:
        name = blob.name.replace(prefix, "").replace(".md", "")
        if name:
            node_ids.append(name)
    return node_ids
