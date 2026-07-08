"""Etsy marketplace adapter."""

import json
import re
from typing import Any, List
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
        stripped = raw_content.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                data = json.loads(stripped)
                listings = self._parse_structured(data)
                if listings:
                    return listings
            except json.JSONDecodeError:
                pass

        soup = BeautifulSoup(raw_content, "lxml")
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                payload = json.loads(script.string or "")
                listings = self._parse_json_ld(payload)
                if listings:
                    return listings
            except (json.JSONDecodeError, TypeError):
                continue

        return self._parse_html_cards(soup)

    def _parse_structured(self, data: Any) -> List[ProductListingSchema]:
        if isinstance(data, list):
            listings: List[ProductListingSchema] = []
            for item in data:
                if isinstance(item, dict):
                    listing = self._listing_from_record(item)
                    if listing:
                        listings.append(listing)
            return listings

        if isinstance(data, dict):
            if "itemListElement" in data:
                return self._parse_json_ld(data)
            listing = self._listing_from_record(data)
            return [listing] if listing else []

        return []

    def _parse_json_ld(self, payload: Any) -> List[ProductListingSchema]:
        if isinstance(payload, list):
            listings: List[ProductListingSchema] = []
            for item in payload:
                listings.extend(self._parse_json_ld(item))
            return listings

        if not isinstance(payload, dict):
            return []

        item_type = payload.get("@type", "")
        if item_type == "Product":
            listing = self._listing_from_record(payload)
            return [listing] if listing else []

        if item_type in ("ItemList", "SearchResultsPage") or "itemListElement" in payload:
            listings: List[ProductListingSchema] = []
            for item in payload.get("itemListElement", []):
                if isinstance(item, dict):
                    product = item.get("item") if isinstance(item.get("item"), dict) else item
                    listing = self._listing_from_record(product)
                    if listing:
                        listings.append(listing)
            return listings

        graph = payload.get("@graph")
        if isinstance(graph, list):
            listings: List[ProductListingSchema] = []
            for node in graph:
                listings.extend(self._parse_json_ld(node))
            return listings

        return []

    def _listing_from_record(self, record: dict) -> ProductListingSchema | None:
        title = (
            record.get("title")
            or record.get("name")
            or record.get("product_name")
            or record.get("listing_title")
        )
        url = record.get("url") or record.get("product_url") or record.get("listing_url") or ""
        if not title and not url:
            return None

        price = self._extract_price(record)
        shop_name = (
            record.get("shop_name")
            or record.get("seller")
            or record.get("store_name")
            or record.get("brand")
            or ""
        )
        if isinstance(shop_name, dict):
            shop_name = shop_name.get("name", "")

        image_url = record.get("image_url") or record.get("image") or ""
        if isinstance(image_url, list):
            image_url = image_url[0] if image_url else ""
        if isinstance(image_url, dict):
            image_url = image_url.get("url", "")

        description = record.get("description") or ""
        tags = record.get("tags") or record.get("keywords") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        rating = record.get("rating", 0.0)
        review_count = record.get("review_count", 0)
        aggregate = record.get("aggregateRating")
        if isinstance(aggregate, dict):
            rating = aggregate.get("ratingValue", rating)
            review_count = aggregate.get("reviewCount", review_count)

        if not title:
            title = "Etsy Listing"

        return ProductListingSchema(
            platform=self.platform_name,
            title=str(title)[:500],
            url=str(url),
            shop_name=str(shop_name),
            price=price,
            currency=record.get("currency") or record.get("priceCurrency") or "USD",
            rating=float(rating or 0.0),
            review_count=int(review_count or 0),
            image_url=str(image_url),
            description=str(description)[:2000],
            tags=[str(tag) for tag in tags][:20],
            detected_keywords=[w.lower() for w in str(title).split() if len(w) > 3],
            raw_data=record,
        )

    def _extract_price(self, record: dict) -> float:
        for key in ("price", "current_price", "listing_price"):
            value = record.get(key)
            parsed = self._parse_price_value(value)
            if parsed is not None:
                return parsed

        offers = record.get("offers")
        if isinstance(offers, dict):
            parsed = self._parse_price_value(offers.get("price") or offers.get("lowPrice"))
            if parsed is not None:
                return parsed
        elif isinstance(offers, list) and offers:
            parsed = self._parse_price_value(offers[0].get("price") if isinstance(offers[0], dict) else offers[0])
            if parsed is not None:
                return parsed

        return 0.0

    def _parse_price_value(self, value: Any) -> float | None:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        match = re.search(r"[\d,.]+", str(value))
        if not match:
            return None
        return float(match.group().replace(",", ""))

    def _parse_html_cards(self, soup: BeautifulSoup) -> List[ProductListingSchema]:
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
