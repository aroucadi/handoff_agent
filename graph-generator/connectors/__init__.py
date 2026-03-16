from __future__ import annotations
from .base import BaseConnector
from .website import WebsiteConnector
from .gcs import GcsConnector
from .document import DocumentConnector
from .zendesk import ZendeskConnector
from .confluence import ConfluenceConnector

CONNECTOR_REGISTRY: dict[str, type[BaseConnector]] = {
    "website_crawl": WebsiteConnector,
    "document_upload": DocumentConnector,
    "zendesk_api": ZendeskConnector,
    "confluence_api": ConfluenceConnector,
    "gcs": GcsConnector, # Internal helper for URI starting with gs://
}

def get_connector(source_type: str, uri: str) -> BaseConnector:
    """Get the appropriate connector for a source type and URI."""
    if uri.startswith("gs://") and source_type == "website_crawl":
        return GcsConnector()
    
    connector_class = CONNECTOR_REGISTRY.get(source_type)
    if not connector_class:
        raise ValueError(f"No connector registered for type: {source_type}")
    return connector_class()
