"""Etsy marketplace adapter."""

import html
import json
import re
from typing import Any, List
from urllib.parse import parse_qs, quote_plus, urlencode, urlparse, urlunparse

from bs4 import BeautifulSoup

from app.adapters.base import BaseMarketplaceAdapter
from app.schemas import ProductListingSchema

LISTING_ID_RE = re.compile(r"/listing/(\d+)")
LISTING_URL_RE = re.compile(r"/listing/\d+")
MARKDOWN_LINK_RE = re.compile(
    r"\[([^\]]+)\]\((https?://(?:www\.)?etsy\.com/listing/\d+[^)]*)\)",
    re.I,
)
JUNK_TITLE_RE = re.compile(
    r"^(add to|favorite|favourite|etsy|shop all|see more|view all|cart|help|sign in|register|search)",
    re.I,
)
MIN_TITLE_LENGTH = 8
ETSY_LOCALE = "en-US"


def with_etsy_locale(url: str, country: str = "") -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    if "locale_override" not in query:
        query["locale_override"] = [ETSY_LOCALE]
    if country and "ship_to" not in query:
        query["ship_to"] = [country]
    flat = {key: values[0] for key, values in query.items() if values}
    return urlunparse(parsed._replace(query=urlencode(flat)))


class EtsyAdapter(BaseMarketplaceAdapter):
    platform_name = "etsy"
    supports_shop_url = True
    supports_product_url = True
    supports_keyword_search = True

    def build_search_url(self, query: str, country: str) -> str:
        url = f"https://www.etsy.com/search?q={quote_plus(query)}"
        return with_etsy_locale(url, country=country)

    def normalize_shop_name(self, value: str) -> str:
        value = value.strip()
        if not value:
            return ""

        match = re.search(r"etsy\.com/shop/([^/?#]+)", value, re.I)
        if match:
            return match.group(1)

        if value.startswith("@"):
            value = value[1:]

        return value.strip().strip("/")

    def build_shop_url(self, shop_name: str, country: str = "US") -> str:
        slug = self.normalize_shop_name(shop_name)
        if not slug:
            raise ValueError("Etsy shop name is required")
        return with_etsy_locale(f"https://www.etsy.com/shop/{slug}", country=country)

    @staticmethod
    def detect_block_page(raw_content: str) -> str | None:
        lowered = raw_content.lower()
        markers = (
            "captcha",
            "datadome",
            "access denied",
            "security check",
            "unusual traffic",
            "verify you are a human",
        )
        if any(marker in lowered for marker in markers):
            return "Etsy returned a bot-protection page instead of search results."
        return None

    def parse_listings(self, raw_content: str) -> List[ProductListingSchema]:
        stripped = raw_content.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            listings = self._parse_structured(self._load_json(stripped))
            if listings:
                return self._dedupe(listings)

        soup = BeautifulSoup(raw_content, "lxml")

        listings: List[ProductListingSchema] = []
        listings.extend(self._parse_all_json_ld(soup))
        listings.extend(self._parse_embedded_scripts(soup))
        listings.extend(self._parse_markdown_listings(raw_content))
        listings.extend(self._parse_html_cards(soup))

        return self.dedupe_listings(listings)

    def dedupe_listings(self, listings: List[ProductListingSchema]) -> List[ProductListingSchema]:
        return self._dedupe([listing for listing in listings if self.is_valid_listing(listing)])

    def enrich_shop_listings(self, listings: List[ProductListingSchema], shop_slug: str) -> List[ProductListingSchema]:
        display_name = shop_slug.replace("-", " ").strip()
        for listing in listings:
            if not listing.shop_name or listing.shop_name.lower() in {"unknown shop", "etsy"}:
                listing.shop_name = display_name
        return listings

    def is_valid_listing(self, listing: ProductListingSchema) -> bool:
        if not self._listing_key(listing.url):
            return False
        title = re.sub(r"\s+", " ", (listing.title or "").strip())
        if len(title) < MIN_TITLE_LENGTH:
            return False
        if JUNK_TITLE_RE.search(title):
            return False
        if title.lower() in {"etsy listing", "listing"}:
            return False
        return True

    def _load_json(self, text: str) -> Any:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _dedupe(self, listings: List[ProductListingSchema]) -> List[ProductListingSchema]:
        seen: set[str] = set()
        unique: List[ProductListingSchema] = []
        for listing in listings:
            key = self._listing_key(listing.url)
            if not key or key in seen:
                continue
            seen.add(key)
            unique.append(listing)
        return unique[:30]

    def _listing_key(self, url: str) -> str:
        match = LISTING_ID_RE.search(url or "")
        return match.group(1) if match else ""

    def _normalize_listing_url(self, href: str) -> str:
        if not href:
            return ""
        path = urlparse(href).path if href.startswith("http") else href.split("?")[0]
        match = LISTING_ID_RE.search(path)
        if not match:
            return ""
        return f"https://www.etsy.com/listing/{match.group(1)}"

    def _parse_all_json_ld(self, soup: BeautifulSoup) -> List[ProductListingSchema]:
        listings: List[ProductListingSchema] = []
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            payload = self._load_json(html.unescape(script.string or script.get_text() or ""))
            if payload is not None:
                listings.extend(self._parse_json_ld(payload))
        return listings

    def _parse_embedded_scripts(self, soup: BeautifulSoup) -> List[ProductListingSchema]:
        listings: List[ProductListingSchema] = []
        for script in soup.find_all("script"):
            script_type = (script.get("type") or "").lower()
            text = html.unescape(script.string or script.get_text() or "").strip()
            if not text:
                continue
            if script_type in {"application/json", "application/ld+json", "text/json"} or text.startswith(("{", "[")):
                payload = self._load_json(text)
                if payload is not None:
                    listings.extend(self._find_listings_in_json(payload))
        return listings

    def _parse_markdown_listings(self, raw_content: str) -> List[ProductListingSchema]:
        listings: List[ProductListingSchema] = []
        for title, url in MARKDOWN_LINK_RE.findall(raw_content):
            normalized = self._normalize_listing_url(url)
            if not normalized:
                continue
            listings.append(ProductListingSchema(
                platform=self.platform_name,
                title=title.strip()[:500] or "Etsy Listing",
                url=normalized,
                shop_name="",
                price=0.0,
                currency="USD",
                rating=0.0,
                review_count=0,
                image_url="",
                description="",
                tags=[],
                detected_keywords=[w.lower() for w in title.split() if len(w) > 3],
            ))
        return listings

    def _parse_structured(self, data: Any) -> List[ProductListingSchema]:
        if data is None:
            return []

        if isinstance(data, list):
            listings: List[ProductListingSchema] = []
            for item in data:
                if isinstance(item, dict):
                    listing = self._listing_from_record(item)
                    if listing:
                        listings.append(listing)
                    else:
                        listings.extend(self._find_listings_in_json(item))
            return listings

        if isinstance(data, dict):
            if "itemListElement" in data:
                return self._parse_json_ld(data)
            listings = self._find_listings_in_json(data)
            if listings:
                return listings
            listing = self._listing_from_record(data)
            return [listing] if listing else []

        return []

    def _find_listings_in_json(self, obj: Any) -> List[ProductListingSchema]:
        found: List[ProductListingSchema] = []

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                if self._looks_like_listing(node):
                    listing = self._listing_from_record(self._normalize_record(node))
                    if listing:
                        found.append(listing)
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(obj)
        return found

    def _looks_like_listing(self, record: dict) -> bool:
        url = str(record.get("url") or record.get("listing_url") or record.get("product_url") or "")
        listing_id = record.get("listing_id") or record.get("listingId") or record.get("id")
        title = record.get("title") or record.get("name") or record.get("listing_title")
        if listing_id and title:
            return True
        return bool(title and LISTING_ID_RE.search(url))

    def _normalize_record(self, record: dict) -> dict:
        normalized = dict(record)
        url = normalized.get("url") or normalized.get("listing_url") or normalized.get("product_url") or ""
        if url and not normalized.get("url"):
            normalized["url"] = url
        listing_id = normalized.get("listing_id") or normalized.get("listingId")
        if listing_id and not normalized.get("url"):
            normalized["url"] = f"https://www.etsy.com/listing/{listing_id}"
        if isinstance(normalized.get("brand"), dict):
            normalized["shop_name"] = normalized["brand"].get("name", "")
        return normalized

    def _is_type(self, payload: dict, *types: str) -> bool:
        value = payload.get("@type", "")
        if isinstance(value, list):
            return any(item in types for item in value)
        return value in types

    def _parse_json_ld(self, payload: Any) -> List[ProductListingSchema]:
        if isinstance(payload, list):
            listings: List[ProductListingSchema] = []
            for item in payload:
                listings.extend(self._parse_json_ld(item))
            return listings

        if not isinstance(payload, dict):
            return []

        if self._is_type(payload, "Product"):
            listing = self._listing_from_record(payload)
            return [listing] if listing else []

        if self._is_type(payload, "ItemList", "SearchResultsPage") or "itemListElement" in payload:
            listings: List[ProductListingSchema] = []
            for item in payload.get("itemListElement", []):
                if not isinstance(item, dict):
                    continue
                if self._is_type(item, "Product"):
                    listing = self._listing_from_record(item)
                elif isinstance(item.get("item"), dict):
                    listing = self._listing_from_record(item["item"])
                else:
                    listing = self._listing_from_record(item)
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
        url = self._normalize_listing_url(str(url)) if url else ""
        if not title and not url:
            return None

        price = self._extract_price(record)
        shop_name = (
            record.get("shop_name")
            or record.get("seller")
            or record.get("store_name")
            or record.get("shop")
            or ""
        )
        if isinstance(shop_name, dict):
            shop_name = shop_name.get("name", "")

        brand = record.get("brand")
        if not shop_name and isinstance(brand, dict):
            shop_name = brand.get("name", "")
        elif not shop_name and isinstance(brand, str):
            shop_name = brand

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
            url=url,
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
        for key in ("price", "current_price", "listing_price", "productPrice"):
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
            first = offers[0]
            parsed = self._parse_price_value(first.get("price") if isinstance(first, dict) else first)
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

    def _card_root(self, element: Any) -> Any:
        for _ in range(6):
            if element is None:
                break
            if element.get("data-listing-id") or element.get("data-palette-listing-id"):
                return element
            element = element.parent
        return None

    def _parse_html_cards(self, soup: BeautifulSoup) -> List[ProductListingSchema]:
        listings: List[ProductListingSchema] = []
        seen: set[str] = set()

        card_roots = soup.select("[data-listing-id], [data-palette-listing-id], .v2-listing-card, .wt-height-full")
        for card in card_roots:
            listing = self._listing_from_card(card)
            if not listing:
                continue
            key = self._listing_key(listing.url)
            if key in seen:
                continue
            seen.add(key)
            listings.append(listing)

        if listings:
            return listings

        for link in soup.find_all("a", href=LISTING_URL_RE):
            listing = self._listing_from_link(link)
            if not listing:
                continue
            key = self._listing_key(listing.url)
            if key in seen:
                continue
            seen.add(key)
            listings.append(listing)

        return listings

    def _listing_from_card(self, card: Any) -> ProductListingSchema | None:
        link = card.find("a", href=LISTING_URL_RE)
        if not link:
            return None
        return self._listing_from_link(link, card)

    def _listing_from_link(self, link: Any, card: Any | None = None) -> ProductListingSchema | None:
        href = link.get("href", "")
        url = self._normalize_listing_url(href)
        if not url:
            return None

        scope = card or self._card_root(link) or link.parent

        title_el = None
        if scope is not None:
            title_el = scope.select_one(
                "h3, h2, [data-listing-card-title], .v2-listing-card__title, .wt-text-caption"
            )
        title = ""
        if title_el:
            title = title_el.get_text(" ", strip=True)
        if not title:
            title = link.get("title") or link.get("aria-label") or link.get_text(" ", strip=True)
        title = re.sub(r"\s+", " ", title).strip()
        if not self.is_valid_listing(ProductListingSchema(platform=self.platform_name, title=title, url=url)):
            return None

        price = 0.0
        if scope is not None:
            price_el = scope.select_one(
                ".lc-price, .n-listing-card__price, .currency-value, [data-price], .wt-text-title-01, .wt-screen-reader-only + .currency-value"
            )
            if price_el:
                parsed = self._parse_price_value(price_el.get_text(" ", strip=True))
                price = parsed or 0.0
            if price <= 0:
                for candidate in scope.select(".currency-value, .lc-price, .wt-text-title-01"):
                    parsed = self._parse_price_value(candidate.get_text(" ", strip=True))
                    if parsed and parsed > 0:
                        price = parsed
                        break

        shop_name = ""
        if scope is not None:
            shop_el = scope.select_one(
                ".v2-listing-card__shop, .shop-name, [data-shop-name], .wt-text-caption.wt-text-link-no-underline"
            )
            if shop_el:
                shop_name = shop_el.get_text(" ", strip=True)

        image_url = ""
        if scope is not None:
            img_el = scope.select_one("img[src]")
            if img_el:
                image_url = img_el.get("src", "")

        rating = 0.0
        if scope is not None:
            rating_el = scope.select_one("[aria-label*='star']")
            if rating_el:
                rating_match = re.search(r"([\d.]+)\s*star", rating_el.get("aria-label", ""), re.I)
                if rating_match:
                    rating = float(rating_match.group(1))

        return ProductListingSchema(
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
        )
