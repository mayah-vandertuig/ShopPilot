"""Marketplace adapter registry."""

from typing import Dict, Type

from app.adapters.amazon import AmazonAdapter
from app.adapters.base import BaseMarketplaceAdapter
from app.adapters.ebay import EbayAdapter
from app.adapters.etsy import EtsyAdapter
from app.adapters.generic_marketplace import GenericMarketplaceAdapter
from app.adapters.google_shopping import GoogleShoppingAdapter
from app.adapters.mock import MockAdapter
from app.adapters.shopee import ShopeeAdapter
from app.adapters.shopify import ShopifyAdapter
from app.adapters.tiktok_shop import TikTokShopAdapter

ADAPTER_REGISTRY: Dict[str, Type[BaseMarketplaceAdapter]] = {
    "etsy": EtsyAdapter,
    "google_shopping": GoogleShoppingAdapter,
    "generic": GenericMarketplaceAdapter,
    "amazon": AmazonAdapter,
    "ebay": EbayAdapter,
    "shopify": ShopifyAdapter,
    "shopee": ShopeeAdapter,
    "tiktok_shop": TikTokShopAdapter,
    "mock": MockAdapter,
}


def get_adapter(platform: str) -> BaseMarketplaceAdapter:
    adapter_cls = ADAPTER_REGISTRY.get(platform, GenericMarketplaceAdapter)
    return adapter_cls()
