"""Data ingestion orchestration."""

from typing import List, Tuple

from app.adapters import get_adapter
from app.exceptions import IngestionError
from app.schemas import InputType, ProductListingSchema
from app.services.bright_data import BrightDataService


class IngestionService:
  def __init__(self):
    self.bright_data = BrightDataService()

  def collect(
    self,
    platform: str,
    input_type: InputType,
    input_value: str,
    country: str,
  ) -> Tuple[List[ProductListingSchema], str, str]:
    """Collect listings from live sources only. Returns (listings, data_source, warning)."""
    adapter = get_adapter(platform)
    last_error = ""

    try:
      if input_type == InputType.keyword and adapter.supports_keyword_search:
        if not self.bright_data.is_available:
          last_error = self.bright_data.unavailable_reason()
        else:
          raw_listings, source, error = self.bright_data.search_marketplace(platform, input_value, country)
          if raw_listings:
            return [adapter.normalize_listing(r) for r in raw_listings], source, ""
          last_error = error or last_error

      elif input_type == InputType.shop_name and platform == "etsy":
        shop_url = adapter.build_shop_url(input_value)
        content, source, error = self.bright_data.scrape_url(shop_url, country=country, platform=platform)
        if content:
          parsed = adapter.parse_listings(content)
          if parsed:
            return parsed, source, ""
          last_error = "Live Etsy shop page scraped but no listings could be parsed"
        elif error:
          last_error = error

      elif input_type == InputType.shop_url and (adapter.supports_shop_url or platform in ("generic", "shopify")):
        content, source, error = self.bright_data.scrape_url(input_value, country=country, platform=platform)
        if content:
          parsed = adapter.parse_listings(content)
          if parsed:
            return parsed, source, ""
          last_error = "Live shop page scraped but no listings could be parsed"
        elif error:
          last_error = error

      elif input_type == InputType.product_url and (adapter.supports_product_url or platform == "generic"):
        content, source, error = self.bright_data.scrape_url(input_value, country=country, platform=platform)
        if content:
          parsed = adapter.parse_listings(content)
          if parsed:
            return parsed, source, ""
          last_error = "Live product page scraped but could not be parsed"
        elif error:
          last_error = error

      elif input_type == InputType.marketplace_url:
        content, source, error = self.bright_data.scrape_url(input_value, country=country, platform=platform)
        generic = get_adapter("generic")
        if content:
          parsed = generic.parse_listings(content)
          if parsed:
            for p in parsed:
              p.platform = platform
            return parsed, source, ""
          last_error = "Live marketplace page scraped but could not be parsed"
        elif error:
          last_error = error
      else:
        if input_type == InputType.shop_name:
          last_error = f"Shop name input is not supported for platform '{platform}'"
        else:
          last_error = f"Input type '{input_type.value}' is not supported for platform '{platform}'"

    except IngestionError:
      raise
    except Exception as e:
      last_error = f"Live data collection failed: {e}"

    if not last_error:
      last_error = self.bright_data.unavailable_reason()

    raise IngestionError(last_error)
