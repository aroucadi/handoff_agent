"""Graph Generator — GCS Storage Module.

Writes generated markdown nodes to Google Cloud Storage.
"""

from __future__ import annotations

from google.cloud import storage as gcs

from config import config


def _get_client() -> gcs.Client:
    """Get GCS client."""
    return gcs.Client(project=config.project_id)


async def write_node_to_gcs(client_id: str, node_id: str, content: str) -> str:
    """Write a single markdown node file to GCS.

    Args:
        client_id: Client identifier for the path prefix.
        node_id: Node identifier (used as filename).
        content: Full markdown content including YAML frontmatter.

    Returns:
        GCS URI of the written file.
    """
    gcs_client = _get_client()
    bucket = gcs_client.bucket(config.skill_graphs_bucket)

    blob_path = f"clients/{client_id}/{node_id}.md"
    blob = bucket.blob(blob_path)
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


async def read_node_from_gcs(client_id: str, node_id: str) -> str | None:
    """Read a single markdown node from GCS.

    Returns None if the node doesn't exist.
    """
    gcs_client = _get_client()
    bucket = gcs_client.bucket(config.skill_graphs_bucket)
    blob_path = f"clients/{client_id}/{node_id}.md"
    blob = bucket.blob(blob_path)

    if not blob.exists():
        # Try without .md extension (for static graph nodes)
        return None

    return blob.download_as_text()


async def read_static_node(layer: str, node_path: str) -> str | None:
    """Read a static (product/industry) node from GCS.

    Args:
        layer: "product" or "industries"
        node_path: Path within the layer, e.g. "index.md" or "manufacturing/cpq-complexity.md"
    """
    gcs_client = _get_client()
    bucket = gcs_client.bucket(config.skill_graphs_bucket)
    blob_path = f"{layer}/{node_path}"
    blob = bucket.blob(blob_path)

    if not blob.exists():
        return None

    return blob.download_as_text()


async def list_client_nodes(client_id: str) -> list[str]:
    """List all node IDs for a client.

    Returns:
        List of node_id strings (without .md extension).
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
