"""Etsy marketplace adapter."""

import re
from typing import List
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.adapters.base import BaseMarketplaceAdapter
from app.schemas import ProductListingSchema


class EtsyAdapter(BaseMarketplaceAdapter):
    platform_name = "etsy"
    supports_shop_url = True
    supports_product_url = True
    supports_keyword_search = True

    def build_search_url(self, query: str, country: str) -> str:
        return f"https://www.etsy.com/search?q={quote_plus(query)}&ship_to={country}"

    def parse_listings(self, raw_content: str) -> List[ProductListingSchema]:
        soup = BeautifulSoup(raw_content, "lxml")
        listings: List[ProductListingSchema] = []

        cards = soup.select("[data-listing-id], .v2-listing-card, .listing-link")
        if not cards:
            cards = soup.find_all("a", href=re.compile(r"/listing/\d+"))

        seen_urls = set()
        for card in cards[:30]:
            try:
                link = card if card.name == "a" else card.find("a", href=re.compile(r"/listing/"))
                if not link:
                    continue
                href = link.get("href", "")
                if not href or href in seen_urls:
                    continue
                seen_urls.add(href)
                url = href if href.startswith("http") else f"https://www.etsy.com{href}"

                title_el = card.select_one("h3, .v2-listing-card__title, [data-listing-card-title]")
                title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True) or "Etsy Listing"

                price_el = card.select_one(".currency-value, .n-listing-card__price, [data-price]")
                price = 0.0
                if price_el:
                    price_match = re.search(r"[\d,.]+", price_el.get_text())
                    if price_match:
                        price = float(price_match.group().replace(",", ""))

                shop_el = card.select_one(".shop-name, [data-shop-name]")
                shop_name = shop_el.get_text(strip=True) if shop_el else ""

                img_el = card.select_one("img")
                image_url = img_el.get("src", "") if img_el else ""

                rating_el = card.select_one("[aria-label*='star'], .star-seller-badge")
                rating = 0.0
                if rating_el:
                    rating_match = re.search(r"([\d.]+)\s*star", rating_el.get("aria-label", ""), re.I)
                    if rating_match:
                        rating = float(rating_match.group(1))

                listings.append(ProductListingSchema(
                    platform=self.platform_name,
                    title=title[:500],
                    url=url,
                    shop_name=shop_name,
                    price=price,
                    currency="USD",
                    rating=rating,
                    review_count=0,
                    image_url=image_url,
                    description="",
                    tags=[],
                    detected_keywords=[w.lower() for w in title.split() if len(w) > 3],
                ))
            except Exception:
                continue

        return listings
