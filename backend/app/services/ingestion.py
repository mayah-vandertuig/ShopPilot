"""Data ingestion orchestration."""

from typing import List, Tuple

from app.adapters import get_adapter
from app.adapters.mock import MockAdapter
from app.schemas import InputType, ProductListingSchema
from app.services.bright_data import BrightDataService


class IngestionService:
  def __init__(self):
    self.bright_data = BrightDataService()
    self.mock = MockAdapter()

  def collect(
    self,
    platform: str,
    input_type: InputType,
    input_value: str,
    country: str,
  ) -> Tuple[List[ProductListingSchema], str, str]:
    """Collect listings. Returns (listings, data_source, warning)."""
    adapter = get_adapter(platform)
    data_source = "mock"
    warning = ""

    try:
      if input_type == InputType.keyword:
        if adapter.supports_keyword_search:
          if self.bright_data.is_available:
            raw_listings, source = self.bright_data.search_marketplace(platform, input_value, country)
            data_source = source
            if raw_listings:
              return [adapter.normalize_listing(r) for r in raw_listings], data_source, warning
          url = adapter.build_search_url(input_value, country)
          content, source = self.bright_data.scrape_url(url)
          data_source = source
          if content:
            parsed = adapter.parse_listings(content)
            if parsed:
              return parsed, data_source, warning

      elif input_type == InputType.shop_url:
        if adapter.supports_shop_url or platform in ("generic", "shopify"):
          content, source = self.bright_data.scrape_url(input_value)
          data_source = source
          if content:
            parsed = adapter.parse_listings(content)
            if parsed:
              return parsed, data_source, warning

      elif input_type == InputType.product_url:
        if adapter.supports_product_url or platform == "generic":
          content, source = self.bright_data.scrape_url(input_value)
          data_source = source
          if content:
            parsed = adapter.parse_listings(content)
            if parsed:
              return parsed, data_source, warning

      elif input_type == InputType.marketplace_url:
        content, source = self.bright_data.scrape_url(input_value)
        data_source = source
        generic = get_adapter("generic")
        if content:
          parsed = generic.parse_listings(content)
          if parsed:
            for p in parsed:
              p.platform = platform
            return parsed, data_source, warning

    except Exception as e:
      warning = f"Live data collection failed: {e}. Using mock data."

    mock_listings = self.mock.get_listings_for_platform(platform, input_value)
    if not warning:
      warning = "Using mock sample data. Set BRIGHT_DATA_API_KEY for live marketplace data."
    return mock_listings, "mock", warning
