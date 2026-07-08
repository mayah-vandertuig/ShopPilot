"""Data ingestion orchestration."""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Set

from app.adapters import get_adapter
from app.adapters.etsy import EtsyAdapter
from app.analysis.competitor_discovery import _shop_key, generate_competitor_queries, is_own_shop
from app.config import get_settings
from app.exceptions import IngestionError
from app.schemas import InputType, ProductListingSchema
from app.services.bright_data import BrightDataService

logger = logging.getLogger(__name__)


@dataclass
class CollectionResult:
    listings: List[ProductListingSchema]
    data_source: str
    warning: str = ""
    competitor_listings: List[ProductListingSchema] = field(default_factory=list)
    user_shop_keys: Set[str] = field(default_factory=set)
    generated_queries: List[str] = field(default_factory=list)


class IngestionService:
    def __init__(self):
        self.bright_data = BrightDataService()
        self.settings = get_settings()

    def collect(
        self,
        platform: str,
        input_type: InputType,
        input_value: str,
        country: str = "",
        currency: str = "",
        language: str = "",
        locale: str = "",
    ) -> CollectionResult:
        """Collect listings from live sources only."""
        country = country or self.settings.default_country
        currency = currency or self.settings.default_currency
        language = language or self.settings.default_language
        locale = locale or self.settings.default_locale

        adapter = get_adapter(platform)
        last_error = ""
        locale_warning = ""

        try:
            if input_type == InputType.keyword and adapter.supports_keyword_search:
                if not self.bright_data.is_available:
                    last_error = self.bright_data.unavailable_reason()
                else:
                    raw_listings, source, error, warning = self.bright_data.search_marketplace(
                        platform,
                        input_value,
                        country=country,
                        currency=currency,
                        language=language,
                        locale=locale,
                    )
                    if warning:
                        locale_warning = warning
                    if raw_listings:
                        listings = [adapter.normalize_listing(r) for r in raw_listings]
                        return CollectionResult(
                            listings=listings,
                            data_source=source,
                            warning=locale_warning,
                        )
                    last_error = error or last_error

            elif input_type == InputType.shop_name and platform == "etsy":
                return self._collect_shop_with_competitors(
                    adapter,
                    input_value,
                    platform="etsy",
                    country=country,
                    currency=currency,
                    language=language,
                    locale=locale,
                )

            elif input_type == InputType.shop_url:
                if platform == "etsy" or "etsy.com" in input_value.lower():
                    etsy_adapter = adapter if platform == "etsy" else get_adapter("etsy")
                    return self._collect_shop_with_competitors(
                        etsy_adapter,
                        input_value,
                        platform="etsy",
                        country=country,
                        currency=currency,
                        language=language,
                        locale=locale,
                    )
                if adapter.supports_shop_url or platform in ("generic", "shopify"):
                    return self._collect_generic_shop_url(
                        adapter,
                        input_value,
                        platform=platform,
                        country=country,
                        currency=currency,
                        language=language,
                        locale=locale,
                    )
                last_error = f"Shop URL input is not supported for platform '{platform}'"

            elif input_type == InputType.product_url and (adapter.supports_product_url or platform == "generic"):
                content, source, error, warning = self.bright_data.scrape_url(
                    input_value,
                    country=country,
                    platform=platform,
                    language=language,
                    currency=currency,
                    locale=locale,
                )
                if warning:
                    locale_warning = warning
                if content:
                    parsed = adapter.parse_listings(content)
                    if parsed:
                        return CollectionResult(
                            listings=parsed,
                            data_source=source,
                            warning=locale_warning,
                        )
                    last_error = "Live product page scraped but could not be parsed"
                elif error:
                    last_error = error

            elif input_type == InputType.marketplace_url:
                content, source, error, warning = self.bright_data.scrape_url(
                    input_value,
                    country=country,
                    platform=platform,
                    language=language,
                    currency=currency,
                    locale=locale,
                )
                generic = get_adapter("generic")
                if warning:
                    locale_warning = warning
                if content:
                    parsed = generic.parse_listings(content)
                    if parsed:
                        for listing in parsed:
                            listing.platform = platform
                        return CollectionResult(
                            listings=parsed,
                            data_source=source,
                            warning=locale_warning,
                        )
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

    def _user_shop_keys(self, shop_slug: str, listings: List[ProductListingSchema]) -> Set[str]:
        keys = {_shop_key(shop_slug)}
        for listing in listings:
            if listing.shop_name:
                keys.add(_shop_key(listing.shop_name))
        return keys

    def _distinct_competitor_shops(
        self,
        listings: List[ProductListingSchema],
        user_shop_keys: Set[str],
    ) -> Set[str]:
        shops: Set[str] = set()
        for listing in listings:
            shop = (listing.shop_name or "").strip()
            if not shop or is_own_shop(shop, user_shop_keys):
                continue
            shops.add(_shop_key(shop))
        return shops

    def _discover_competitor_listings(
        self,
        platform: str,
        adapter,
        shop_slug: str,
        user_listings: List[ProductListingSchema],
        country: str,
        currency: str,
        language: str,
        locale: str,
    ) -> tuple[List[ProductListingSchema], str, str, List[str]]:
        user_shop_keys = self._user_shop_keys(shop_slug, user_listings)
        queries = generate_competitor_queries(user_listings, shop_slug)
        logger.info(
            "Competitor discovery for shop=%s user_listings=%d generated_queries=%s",
            shop_slug,
            len(user_listings),
            queries,
        )
        competitor_listings: List[ProductListingSchema] = []
        warning = ""
        data_source = "live"

        shop_keys_match = getattr(adapter, "shop_keys_match", None)
        is_valid = getattr(adapter, "is_valid_listing", lambda listing: bool(listing.title and listing.title.strip()))
        dedupe = getattr(adapter, "dedupe_listings", lambda listings: listings)
        finalize = getattr(adapter, "finalize_listings", lambda listings: listings)

        if self.bright_data.is_available:
            for query in queries[:3]:
                if len(competitor_listings) >= 24:
                    break
                if len(self._distinct_competitor_shops(competitor_listings, user_shop_keys)) >= 4:
                    break
                raw_listings, source, error, comp_warning = self.bright_data.search_marketplace(
                    platform,
                    query,
                    country=country,
                    currency=currency,
                    language=language,
                    locale=locale,
                    fast=True,
                )
                if comp_warning and not warning:
                    warning = comp_warning
                if not raw_listings:
                    continue
                for position, raw in enumerate(raw_listings):
                    listing = adapter.normalize_listing(raw)
                    if not is_valid(listing):
                        continue
                    if shop_keys_match and shop_keys_match(listing.shop_name, shop_slug):
                        continue
                    if is_own_shop(listing.shop_name, user_shop_keys):
                        continue
                    listing.raw_data = {
                        **(listing.raw_data or {}),
                        "matched_query": query,
                        "search_position": position,
                        "listing_source": "competitor_search",
                    }
                    listing.listing_source = "competitor_search"
                    competitor_listings.append(listing)
                competitor_listings = finalize(dedupe(competitor_listings))

        scraped_count = len(competitor_listings)
        distinct_shops = self._distinct_competitor_shops(competitor_listings, user_shop_keys)
        after_exclusion_count = len([
            listing for listing in competitor_listings
            if not is_own_shop(listing.shop_name, user_shop_keys) and listing.shop_name.strip()
        ])
        logger.info(
            "Competitor scrape results shop=%s scraped=%d after_exclusion=%d distinct_shops=%d",
            shop_slug,
            scraped_count,
            after_exclusion_count,
            len(distinct_shops),
        )

        if not distinct_shops:
            warning = warning or (
                "Marketplace search did not return enough similar competitor shops. "
                "Only live search results are used for competitor discovery."
            )
            logger.info(
                "No distinct competitor shops found shop=%s scraped=%d queries=%s",
                shop_slug,
                scraped_count,
                queries[:3],
            )

        return competitor_listings, warning, data_source, queries

    def _collect_shop_with_competitors(
        self,
        adapter: EtsyAdapter,
        input_value: str,
        platform: str,
        country: str,
        currency: str,
        language: str,
        locale: str,
    ) -> CollectionResult:
        shop_slug = adapter.normalize_shop_name(input_value)
        if not shop_slug:
            raise IngestionError("Enter a valid Etsy shop name.")

        shop_url = (
            input_value
            if input_value.strip().lower().startswith("http")
            else adapter.build_shop_url(
                input_value,
                country=country,
                currency=currency,
                language=language,
            )
        )

        if not self.bright_data.is_available:
            raise IngestionError(self.bright_data.unavailable_reason())

        content, source, error, locale_warning = self.bright_data.scrape_url(
            shop_url,
            country=country,
            platform=platform,
            language=language,
            currency=currency,
            locale=locale,
        )
        if not content:
            raise IngestionError(error or "Failed to scrape shop page")

        block_reason = adapter.detect_block_page(content)
        if block_reason:
            raise IngestionError(block_reason)

        parsed = adapter.enrich_shop_listings(adapter.parse_listings(content), shop_slug)
        parsed = adapter.enrich_listing_tags(parsed, content)
        if any(not listing.tags for listing in parsed):
            parsed = adapter.enrich_listings_from_detail_pages(
                parsed,
                self.bright_data,
                country=country,
                currency=currency,
                language=language,
                locale=locale,
                max_listings=2,
                fast=True,
            )
        parsed = [listing for listing in parsed if adapter.is_valid_listing(listing)]
        if not parsed:
            raise IngestionError(
                "Live shop page could not be parsed. "
                "The marketplace HTML may have changed or blocked the request."
            )

        warning = locale_warning or ""
        competitor_listings, comp_warning, comp_source, queries = self._discover_competitor_listings(
            platform,
            adapter,
            shop_slug,
            parsed,
            country,
            currency,
            language,
            locale,
        )
        if comp_warning:
            warning = f"{warning} {comp_warning}".strip() if warning else comp_warning
        if not competitor_listings:
            warning = warning or (
                "Only this shop's listings were found. Discovered competitors use marketplace search when available."
            )

        data_source = source if comp_source == "live" else comp_source
        return CollectionResult(
            listings=parsed,
            data_source=data_source,
            warning=warning,
            competitor_listings=competitor_listings,
            user_shop_keys=self._user_shop_keys(shop_slug, parsed),
            generated_queries=queries,
        )

    def _collect_generic_shop_url(
        self,
        adapter,
        shop_url: str,
        platform: str,
        country: str,
        currency: str,
        language: str,
        locale: str,
    ) -> CollectionResult:
        if not self.bright_data.is_available:
            raise IngestionError(self.bright_data.unavailable_reason())

        content, source, error, locale_warning = self.bright_data.scrape_url(
            shop_url,
            country=country,
            platform=platform,
            language=language,
            currency=currency,
            locale=locale,
        )
        if not content:
            raise IngestionError(error or "Failed to scrape shop page")

        parsed = adapter.parse_listings(content)
        if not parsed:
            raise IngestionError("Live shop page scraped but no listings could be parsed")

        shop_slug = parsed[0].shop_name or shop_url.rstrip("/").split("/")[-1]
        warning = locale_warning or ""
        competitor_listings: List[ProductListingSchema] = []
        comp_source = source
        queries: List[str] = []

        if adapter.supports_keyword_search:
            competitor_listings, comp_warning, comp_source, queries = self._discover_competitor_listings(
                platform,
                adapter,
                shop_slug,
                parsed,
                country,
                currency,
                language,
                locale,
            )
            if comp_warning:
                warning = f"{warning} {comp_warning}".strip() if warning else comp_warning

        return CollectionResult(
            listings=parsed,
            data_source=comp_source if competitor_listings else source,
            warning=warning,
            competitor_listings=competitor_listings,
            user_shop_keys=self._user_shop_keys(shop_slug, parsed),
            generated_queries=queries,
        )
