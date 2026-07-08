"""Google Shopping adapter."""

import re
from typing import List
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.adapters.base import BaseMarketplaceAdapter
from app.schemas import ProductListingSchema
from app.services.marketplace_url import normalize_marketplace_url


class GoogleShoppingAdapter(BaseMarketplaceAdapter):
    platform_name = "google_shopping"
    supports_shop_url = False
    supports_product_url = False
    supports_keyword_search = True

    def build_search_url(
        self,
        query: str,
        country: str = "US",
        currency: str = "USD",
        language: str = "en-US",
        locale: str = "en_US",
    ) -> str:
        url = f"https://www.google.com/search?tbm=shop&q={quote_plus(query)}"
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

        cards = soup.select(".sh-dgr__content, .i0Xnmd, [data-docid], .rg_sho")
        if not cards:
            cards = soup.find_all("div", class_=re.compile(r"sh-|product"))

        for card in cards[:30]:
            try:
                title_el = card.select_one("h3, h4, .tAxDx, [role='heading']")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue

                price_el = card.select_one(".a8Pemb, .e10twf, [aria-label*='$']")
                price = 0.0
                if price_el:
                    price_match = re.search(r"[\d,.]+", price_el.get_text())
                    if price_match:
                        price = float(price_match.group().replace(",", ""))

                link_el = card.find("a", href=True)
                url = link_el["href"] if link_el else ""

                shop_el = card.select_one(".aULzUe, .IuHnof")
                shop_name = shop_el.get_text(strip=True) if shop_el else "Google Shopping"

                img_el = card.select_one("img")
                image_url = img_el.get("src", "") if img_el else ""

                listings.append(ProductListingSchema(
                    platform=self.platform_name,
                    title=title[:500],
                    url=url,
                    shop_name=shop_name,
                    price=price,
                    currency="USD",
                    rating=0.0,
                    review_count=0,
                    image_url=image_url,
                    description="",
                    tags=[],
                    detected_keywords=[w.lower() for w in title.split() if len(w) > 3],
                ))
            except Exception:
                continue

        return listings
