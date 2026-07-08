"""Bright Data integration service."""

import logging
from typing import Dict, List, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)


class BrightDataService:
  def __init__(self):
    self.settings = get_settings()
    self._client = None

  @property
  def is_available(self) -> bool:
    return self.settings.has_bright_data

  def _get_client(self):
    if self._client is None and self.is_available:
      try:
        from brightdata import SyncBrightDataClient
        self._client = SyncBrightDataClient(token=self.settings.bright_data_api_key)
      except Exception as e:
        logger.warning("Bright Data client init failed: %s", e)
    return self._client

  def scrape_url(self, url: str) -> tuple[str, str]:
    """Scrape URL. Returns (content, data_source)."""
    client = self._get_client()
    if not client:
      return "", "mock"
    try:
      result = client.scrape_url(url)
      html_or_text = result.data if hasattr(result, "data") else str(result)
      return html_or_text or "", "live"
    except Exception as e:
      logger.warning("Bright Data scrape failed for %s: %s", url, e)
      return "", "mock"

  def search_marketplace(self, platform: str, query: str, country: str) -> tuple[List[dict], str]:
    from app.adapters import get_adapter

    adapter = get_adapter(platform)
    url = adapter.build_search_url(query, country)
    content, source = self.scrape_url(url)
    if not content:
      return [], "mock"
    listings = adapter.parse_listings(content)
    if not listings:
      return [], "mock"
    return [l.model_dump() for l in listings], source

  def scrape_shop(self, platform: str, shop_url: str) -> tuple[List[dict], str]:
    from app.adapters import get_adapter

    content, source = self.scrape_url(shop_url)
    if not content:
      return [], "mock"
    adapter = get_adapter(platform)
    listings = adapter.parse_listings(content)
    if not listings:
      return [], "mock"
    return [l.model_dump() for l in listings], source

  def scrape_product(self, platform: str, product_url: str) -> tuple[Optional[dict], str]:
    from app.adapters import get_adapter

    content, source = self.scrape_url(product_url)
    if not content:
      return None, "mock"
    adapter = get_adapter(platform)
    listings = adapter.parse_listings(content)
    if listings:
      return listings[0].model_dump(), source
    return None, "mock"
