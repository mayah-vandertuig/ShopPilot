"""Shopify store adapter stub."""

from typing import List

from app.adapters.base import BaseMarketplaceAdapter
from app.adapters.generic_marketplace import GenericMarketplaceAdapter
from app.schemas import ProductListingSchema


class ShopifyAdapter(BaseMarketplaceAdapter):
    platform_name = "shopify"
    supports_shop_url = True
    supports_product_url = True
    supports_keyword_search = False
    not_implemented_message = "Shopify adapter is not fully implemented yet. Using generic extraction fallback."

    def __init__(self):
        self._fallback = GenericMarketplaceAdapter()
        self._fallback.platform_name = self.platform_name

    def build_search_url(self, query: str, country: str) -> str:
        return f"https://www.google.com/search?q=site:myshopify.com+{query}"

    def parse_listings(self, raw_content: str) -> List[ProductListingSchema]:
        listings = self._fallback.parse_listings(raw_content)
        for listing in listings:
            listing.platform = self.platform_name
        return listings
