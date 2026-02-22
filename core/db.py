"""Synapse Core Library — Database Client Singleton.

Provides a unified, reusable Google Cloud Firestore client to prevent
repeated inline instantiations and enable connection pooling across
the application modules.
"""

from typing import Optional
from google.cloud import firestore
from google.cloud.firestore import AsyncClient

from core.config import config


# Global singleton instances
_firestore_client: Optional[firestore.Client] = None
_firestore_async_client: Optional[AsyncClient] = None


def get_firestore_client() -> firestore.Client:
    """Get or create the synchronous Firestore client singleton."""
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client(project=config.project_id)
    return _firestore_client


def get_firestore_async_client() -> AsyncClient:
    """Get or create the asynchronous Firestore client singleton."""
    global _firestore_async_client
    if _firestore_async_client is None:
        _firestore_async_client = AsyncClient(project=config.project_id)
    return _firestore_async_client
