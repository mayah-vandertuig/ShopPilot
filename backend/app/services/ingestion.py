"""Data ingestion orchestration."""

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import List

from app.adapters import get_adapter
from app.adapters.etsy import EtsyAdapter
from app.exceptions import IngestionError
from app.schemas import InputType, ProductListingSchema
from app.services.bright_data import BrightDataService


@dataclass
class CollectionResult:
    listings: List[ProductListingSchema]
    data_source: str
    warning: str = ""
    competitor_listings: List[ProductListingSchema] = field(default_factory=list)


class IngestionService:
    def __init__(self):
        self.bright_data = BrightDataService()

    def collect(
        self,
        platform: str,
        input_type: InputType,
        input_value: str,
        country: str,
    ) -> CollectionResult:
        """Collect listings from live sources only."""
        adapter = get_adapter(platform)
        last_error = ""

        try:
            if input_type == InputType.keyword and adapter.supports_keyword_search:
                if not self.bright_data.is_available:
                    last_error = self.bright_data.unavailable_reason()
                else:
                    raw_listings, source, error = self.bright_data.search_marketplace(platform, input_value, country)
                    if raw_listings:
                        listings = [adapter.normalize_listing(r) for r in raw_listings]
                        return CollectionResult(listings=listings, data_source=source)
                    last_error = error or last_error

            elif input_type == InputType.shop_name and platform == "etsy":
                return self._collect_etsy_shop(adapter, input_value, country)

            elif input_type == InputType.shop_url and (adapter.supports_shop_url or platform in ("generic", "shopify")):
                content, source, error = self.bright_data.scrape_url(input_value, country=country, platform=platform)
                if content:
                    parsed = adapter.parse_listings(content)
                    if parsed:
                        return CollectionResult(listings=parsed, data_source=source)
                    last_error = "Live shop page scraped but no listings could be parsed"
                elif error:
                    last_error = error

            elif input_type == InputType.product_url and (adapter.supports_product_url or platform == "generic"):
                content, source, error = self.bright_data.scrape_url(input_value, country=country, platform=platform)
                if content:
                    parsed = adapter.parse_listings(content)
                    if parsed:
                        return CollectionResult(listings=parsed, data_source=source)
                    last_error = "Live product page scraped but could not be parsed"
                elif error:
                    last_error = error

            elif input_type == InputType.marketplace_url:
                content, source, error = self.bright_data.scrape_url(input_value, country=country, platform=platform)
                generic = get_adapter("generic")
                if content:
                    parsed = generic.parse_listings(content)
                    if parsed:
                        for listing in parsed:
                            listing.platform = platform
                        return CollectionResult(listings=parsed, data_source=source)
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

    def _collect_etsy_shop(self, adapter: EtsyAdapter, input_value: str, country: str) -> CollectionResult:
        shop_slug = adapter.normalize_shop_name(input_value)
        shop_url = adapter.build_shop_url(input_value, country=country)
        content, source, error = self.bright_data.scrape_url(shop_url, country=country, platform="etsy")
        if not content:
            raise IngestionError(error or "Failed to scrape Etsy shop page")

        block_reason = adapter.detect_block_page(content)
        if block_reason:
            raise IngestionError(block_reason)

        parsed = adapter.enrich_shop_listings(adapter.parse_listings(content), shop_slug)
        parsed = adapter.enrich_listing_tags(parsed, content)
        parsed = adapter.enrich_listings_from_detail_pages(parsed, self.bright_data, country=country, max_listings=6)
        parsed = [listing for listing in parsed if adapter.is_valid_listing(listing)]
        if not parsed:
            raise IngestionError(
                "Live Etsy shop page was scraped but no product listings could be parsed. "
                "The shop may be empty or Etsy blocked the request."
            )

        warning = ""
        competitor_listings: List[ProductListingSchema] = []
        comp_error: str | None = None
        target = shop_slug.lower()

        queries: List[str] = []
        primary_query = self._etsy_competitor_search_query(shop_slug, parsed)
        if primary_query:
            queries.append(primary_query)
        slug_query = shop_slug.replace("-", " ").replace("_", " ").strip()
        if slug_query and slug_query not in queries:
            queries.append(slug_query)

        for query in queries:
            if len(competitor_listings) >= 12:
                break
            raw_competitors, _, error = self.bright_data.search_marketplace("etsy", query, country)
            if error and not comp_error:
                comp_error = error
            if not raw_competitors:
                continue
            for raw in raw_competitors:
                listing = adapter.normalize_listing(raw)
                comp_slug = adapter.normalize_shop_name(listing.shop_name).lower()
                if comp_slug and comp_slug != target and adapter.is_valid_listing(listing):
                    competitor_listings.append(listing)
            competitor_listings = adapter.dedupe_listings(competitor_listings)

        if comp_error and not competitor_listings:
            warning = (
                "Shop listings loaded, but comparable Etsy search results were unavailable. "
                "Competitor metrics may be limited."
            )

        if not competitor_listings:
            warning = warning or (
                "Only this shop's listings were found. Competitor benchmarks use Etsy search when available."
            )

        return CollectionResult(
            listings=parsed,
            data_source=source,
            warning=warning,
            competitor_listings=competitor_listings,
        )

    def _etsy_competitor_search_query(self, shop_slug: str, listings: List[ProductListingSchema]) -> str:
        words: List[str] = []
        for listing in listings[:8]:
            words.extend(re.findall(r"[a-zA-Z]{4,}", listing.title.lower()))
        if words:
            common = [word for word, _ in Counter(words).most_common(4)]
            return " ".join(common)
        return shop_slug.replace("-", " ").replace("_", " ")
