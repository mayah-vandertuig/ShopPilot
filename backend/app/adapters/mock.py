"""Mock adapter using seed data."""

import json
from pathlib import Path
from typing import List

from app.adapters.base import BaseMarketplaceAdapter
from app.schemas import ProductListingSchema

SEED_PATH = Path(__file__).resolve().parent.parent / "seed" / "sample_marketplace_data.json"


class MockAdapter(BaseMarketplaceAdapter):
    platform_name = "mock"
    supports_shop_url = True
    supports_product_url = True
    supports_keyword_search = True

    def build_search_url(self, query: str, country: str) -> str:
        return f"https://mock.shoppilot.local/search?q={query}&country={country}"

    def load_seed_data(self) -> List[dict]:
        if SEED_PATH.exists():
            with open(SEED_PATH) as f:
                data = json.load(f)
                return data.get("listings", [])
        return []

    def parse_listings(self, raw_content: str) -> List[ProductListingSchema]:
        listings = self.load_seed_data()
        return [self.normalize_listing(item) for item in listings]

    def get_listings_for_platform(self, platform: str, query: str = "") -> List[ProductListingSchema]:
        listings = self.load_seed_data()
        filtered = [l for l in listings if l.get("platform", platform) == platform or platform == "mock"]
        if not filtered:
            filtered = listings
        if query:
            words = [w.lower() for w in query.split() if len(w) > 2]
            if words:
                scored = []
                for l in filtered:
                    text = f"{l.get('title', '')} {' '.join(l.get('tags', []))}".lower()
                    if any(w in text for w in words):
                        scored.append(l)
                if len(scored) >= 5:
                    filtered = scored
        return [self.normalize_listing(item) for item in filtered]
