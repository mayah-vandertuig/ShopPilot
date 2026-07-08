"""Generic marketplace adapter for unknown URLs."""

import re
from typing import List
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.adapters.base import BaseMarketplaceAdapter
from app.schemas import ProductListingSchema
from app.services.marketplace_url import normalize_marketplace_url


class GenericMarketplaceAdapter(BaseMarketplaceAdapter):
    platform_name = "generic"
    supports_shop_url = True
    supports_product_url = True
    supports_keyword_search = False

    def build_search_url(
        self,
        query: str,
        country: str = "US",
        currency: str = "USD",
        language: str = "en-US",
        locale: str = "en_US",
    ) -> str:
        url = f"https://www.google.com/search?q={query}"
        return normalize_marketplace_url(
            url,
            platform=self.platform_name,
            country=country,
            language=language,
            currency=currency,
            locale=locale,
        )

    def parse_listings(self, raw_content: str) -> List[ProductListingSchema]:
        soup = BeautifulSoup(raw_content, "lxml")
        listings: List[ProductListingSchema] = []
        text = soup.get_text(" ", strip=True)

        price_matches = re.findall(r"\$[\d,.]+", text)
        titles = []

        for tag in soup.find_all(["h1", "h2", "h3", "a"]):
            t = tag.get_text(strip=True)
            if 10 < len(t) < 200 and any(kw in t.lower() for kw in ["art", "print", "poster", "canvas", "wall"]):
                titles.append(t)

        if not titles:
            titles = [t.get_text(strip=True) for t in soup.find_all("h2")[:10]]

        domain = ""
        og_url = soup.find("meta", property="og:url")
        if og_url:
            domain = urlparse(og_url.get("content", "")).netloc

        for i, title in enumerate(titles[:15]):
            price = 0.0
            if i < len(price_matches):
                price = float(price_matches[i].replace("$", "").replace(",", ""))
            listings.append(ProductListingSchema(
                platform=self.platform_name,
                title=title[:500],
                url=og_url.get("content", "") if og_url else "",
                shop_name=domain or "Unknown Shop",
                price=price,
                currency="USD",
                rating=0.0,
                review_count=0,
                image_url="",
                description=text[:500] if i == 0 else "",
                tags=[],
                detected_keywords=[w.lower() for w in title.split() if len(w) > 3],
            ))

        return listings
