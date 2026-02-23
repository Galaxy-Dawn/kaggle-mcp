"""Kaggle API client wrapper using kagglesdk."""

import logging

from kagglesdk import KaggleClient

logger = logging.getLogger(__name__)

_client: KaggleClient | None = None


def get_client() -> KaggleClient:
    """Get authenticated KaggleClient instance (lazy init)."""
    global _client
    if _client is None:
        _client = KaggleClient()
    return _client
