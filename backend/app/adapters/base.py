"""Marketplace adapter base class."""

from abc import ABC, abstractmethod
from typing import List

from app.schemas import ProductListingSchema


class BaseMarketplaceAdapter(ABC):
    platform_name: str = "unknown"
    supports_shop_url: bool = False
    supports_product_url: bool = False
    supports_keyword_search: bool = False
    not_implemented_message: str = ""

    @abstractmethod
    def build_search_url(
        self,
        query: str,
        country: str = "US",
        currency: str = "USD",
        language: str = "en-US",
        locale: str = "en_US",
    ) -> str:
        pass

    @abstractmethod
    def parse_listings(self, raw_content: str) -> List[ProductListingSchema]:
        pass

    def dedupe_listings(self, listings: List[ProductListingSchema]) -> List[ProductListingSchema]:
        seen: set[str] = set()
        unique: List[ProductListingSchema] = []
        for listing in listings:
            key = listing.url or listing.title
            if key in seen:
                continue
            seen.add(key)
            unique.append(listing)
        return unique

    def normalize_listing(self, raw: dict) -> ProductListingSchema:
        return ProductListingSchema(
            platform=raw.get("platform", self.platform_name),
            title=raw.get("title", "Untitled"),
            url=raw.get("url", ""),
            shop_name=raw.get("shop_name", ""),
            price=float(raw.get("price", 0) or 0),
            currency=raw.get("currency", "USD"),
            rating=float(raw.get("rating", 0) or 0),
            review_count=int(raw.get("review_count", 0) or 0),
            image_url=raw.get("image_url", ""),
            description=raw.get("description", ""),
            tags=raw.get("tags", []) or [],
            detected_keywords=raw.get("detected_keywords", []) or [],
            raw_data=raw,
        )

    def is_stub(self) -> bool:
        return bool(self.not_implemented_message)
