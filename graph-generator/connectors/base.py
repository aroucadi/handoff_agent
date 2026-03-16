from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class BaseConnector(ABC):
    """Abstract base class for all knowledge source connectors."""
    
    @abstractmethod
    async def fetch_pages(self, uri: str, config: dict[str, Any] = None) -> list[dict[str, Any]]:
        """Fetch raw content from the source and return a list of pages.
        
        Args:
            uri: The URI of the knowledge source.
            config: Optional connector-specific configuration.
            
        Returns:
            List of dicts: {"url": str, "title": str, "category": str, "text_content": str}
        """
        pass
