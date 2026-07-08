"""Etsy marketplace adapter."""

import html
import json
import re
from typing import Any, List
from urllib.parse import parse_qs, quote_plus, unquote, urlencode, urlparse, urlunparse

from bs4 import BeautifulSoup

from app.adapters.base import BaseMarketplaceAdapter
from app.schemas import ProductListingSchema

LISTING_ID_RE = re.compile(r"/listing/(\d+)")
LISTING_URL_RE = re.compile(r"/listing/\d+")
MARKET_TAG_RE = re.compile(r"/market/([^/?#]+)")
MARKDOWN_LINK_RE = re.compile(
    r"\[([^\]]+)\]\((https?://(?:www\.)?etsy\.com/listing/\d+[^)]*)\)",
    re.I,
)
JUNK_TITLE_RE = re.compile(
    r"^(add to|favorite|favorites|favourite|favourites|etsy|shop all|see more|view all|cart|help|sign in|register|search|"
    r"añadir|agregar|anadir|favorito|favoritos|carrito|ver más|ver mas|ver todo|iniciar sesión|iniciar sesion|"
    r"registrarse|buscar|ayuda|tienda|artículo|articulo|envío|envio|comprar|vendido|explorar)",
    re.I,
)
MIN_TITLE_LENGTH = 8
DEFAULT_ETSY_LANGUAGE = "en-US"
TAG_JUNK = {
    "free shipping", "etsy", "handmade", "personalized", "custom", "sale", "new",
    "add to cart", "shop all", "view all",
}
SPANISH_TAG_RE = re.compile(
    r"[áéíóúñü]|"
    r"\b(arte|pared|minimalista|impresi[oó]n|cartel|decoraci[oó]n|descarga|"
    r"gratis|tienda|comprar|vendido|favoritos|buscar|cartel|p[oó]ster)\b",
    re.I,
)
TAG_OBJECT_SLUG_KEYS = ("slug", "tag_slug", "machine_name", "canonical", "normalized", "id")
TAG_OBJECT_NAME_KEYS = ("tag", "name", "label", "text", "value", "title")


def with_etsy_locale(
    url: str,
    country: str = "US",
    currency: str = "USD",
    language: str = DEFAULT_ETSY_LANGUAGE,
) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query["locale_override"] = [language or DEFAULT_ETSY_LANGUAGE]
    if country:
        query["ship_to"] = [country]
    query["currency"] = [currency or "USD"]
    flat = {key: values[0] for key, values in query.items() if values}
    return urlunparse(parsed._replace(query=urlencode(flat)))


class EtsyAdapter(BaseMarketplaceAdapter):
    platform_name = "etsy"
    supports_shop_url = True
    supports_product_url = True
    supports_keyword_search = True

    def build_search_url(
        self,
        query: str,
        country: str = "US",
        currency: str = "USD",
        language: str = DEFAULT_ETSY_LANGUAGE,
        locale: str = "en_US",
    ) -> str:
        url = f"https://www.etsy.com/search?q={quote_plus(query)}"
        return with_etsy_locale(url, country=country, currency=currency, language=language)

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

    def shop_slug_key(self, value: str) -> str:
        slug = self.normalize_shop_name(value).lower()
        return re.sub(r"[\s_\-]+", "", slug)

    def shop_keys_match(self, left: str, right: str) -> bool:
        left_key = self.shop_slug_key(left)
        right_key = self.shop_slug_key(right)
        return bool(left_key) and left_key == right_key

    def _tag_from_link_href(self, href: str) -> str | None:
        if not href:
            return None

        parsed = urlparse(href)
        query = parse_qs(parsed.query)
        for key in ("tags", "tag"):
            values = query.get(key) or []
            if values and values[0].strip():
                return unquote(values[0].replace("+", " ")).strip()

        market_match = MARKET_TAG_RE.search(parsed.path)
        if market_match:
            slug = unquote(market_match.group(1))
            return re.sub(r"[_-]+", " ", slug).strip()

        return None

    def build_shop_url(
        self,
        shop_name: str,
        country: str = "US",
        currency: str = "USD",
        language: str = DEFAULT_ETSY_LANGUAGE,
    ) -> str:
        slug = self.normalize_shop_name(shop_name)
        if not slug:
            raise ValueError("Etsy shop name is required")
        return with_etsy_locale(
            f"https://www.etsy.com/shop/{slug}",
            country=country,
            currency=currency,
            language=language,
        )

    @staticmethod
    def detect_block_page(raw_content: str) -> str | None:
        if LISTING_ID_RE.search(raw_content):
            return None

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
            return "Etsy returned a bot-protection page instead of shop results."
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
        return self.finalize_listings(self._dedupe([listing for listing in listings if self.is_valid_listing(listing)]))

    def enrich_shop_listings(self, listings: List[ProductListingSchema], shop_slug: str) -> List[ProductListingSchema]:
        display_name = shop_slug.replace("-", " ").strip()
        for listing in listings:
            if not listing.shop_name or listing.shop_name.lower() in {"unknown shop", "etsy"}:
                listing.shop_name = display_name
        return listings

    def enrich_listing_tags(self, listings: List[ProductListingSchema], raw_content: str) -> List[ProductListingSchema]:
        tag_index = self._build_tag_index(raw_content)
        for listing in listings:
            listing_id = self._listing_key(listing.url)
            if listing_id and listing_id in tag_index:
                listing.tags = tag_index[listing_id]
            elif listing.raw_data:
                listing.tags = self._tags_from_record(listing.raw_data)
        return self.finalize_listings(listings)

    def enrich_listings_from_detail_pages(
        self,
        listings: List[ProductListingSchema],
        bright_data: Any,
        country: str = "US",
        currency: str = "USD",
        language: str = DEFAULT_ETSY_LANGUAGE,
        locale: str = "en_US",
        max_listings: int = 8,
        fast: bool = False,
    ) -> List[ProductListingSchema]:
        if bright_data is None or not getattr(bright_data, "is_available", False):
            return self.finalize_listings(listings)

        enriched = 0
        for listing in listings:
            if listing.tags or not listing.url or enriched >= max_listings:
                continue
            detail_url = with_etsy_locale(listing.url, country=country, currency=currency, language=language)
            content, _, error, _ = bright_data.scrape_url(
                detail_url,
                country=country,
                platform="etsy",
                language=language,
                currency=currency,
                locale=locale,
                fast=fast,
            )
            if not content or error:
                continue
            tags = self.parse_listing_page_tags(content)
            if tags:
                listing.tags = tags
                enriched += 1
        return self.finalize_listings(listings)

    def parse_listing_page_tags(self, raw_content: str) -> List[str]:
        tags: List[str] = []
        soup = BeautifulSoup(raw_content, "lxml")

        for link in soup.select("a.wt-tag, a[data-tag], a[href*='tags='], a[href*='/market/']"):
            href = link.get("href", "")
            tag = self._tag_from_link_href(href)
            if tag:
                tags.append(tag)

        return self._dedupe_tags(tags)

    def finalize_listings(self, listings: List[ProductListingSchema]) -> List[ProductListingSchema]:
        for listing in listings:
            listing.shop_name = self._resolve_shop_name(listing.shop_name, listing.url, listing.raw_data)
            listing.tags = self._dedupe_tags(listing.tags)
            listing.detected_keywords = [
                word.lower()
                for word in re.findall(r"[a-zA-Z]{3,}", listing.title)
                if word.lower() not in {"the", "and", "for", "with", "from", "your", "etsy"}
            ][:15]
        return listings

    def _resolve_shop_name(self, shop_name: str, url: str, raw_data: dict | None) -> str:
        if shop_name and shop_name.lower() not in {"unknown shop", "etsy", ""}:
            return shop_name
        if isinstance(raw_data, dict):
            for key in ("shop_name", "seller", "store_name", "shop", "shop_slug", "shopName"):
                value = raw_data.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
                if isinstance(value, dict) and value.get("name"):
                    return str(value["name"]).strip()
        return shop_name or ""

    def _looks_like_localized_tag(self, value: str) -> bool:
        cleaned = re.sub(r"\s+", " ", (value or "").strip())
        if not cleaned:
            return True
        return bool(SPANISH_TAG_RE.search(cleaned))

    def _canonical_tag_value(self, item: Any) -> str | None:
        if isinstance(item, dict):
            for key in TAG_OBJECT_SLUG_KEYS:
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    if key in {"href", "url"}:
                        return self._tag_from_link_href(value)
                    return re.sub(r"[_-]+", " ", unquote(value)).strip()

            href = item.get("href") or item.get("url")
            if isinstance(href, str) and href.strip():
                tag = self._tag_from_link_href(href)
                if tag:
                    return tag

            for key in TAG_OBJECT_NAME_KEYS:
                value = item.get(key)
                if isinstance(value, str) and value.strip() and not self._looks_like_localized_tag(value):
                    return value.strip()
            return None

        if isinstance(item, str):
            cleaned = item.strip()
            if cleaned and not self._looks_like_localized_tag(cleaned):
                return cleaned
        return None

    def _tags_from_record(self, record: dict) -> List[str]:
        tags: List[str] = []
        for key in ("tags", "tag_list"):
            value = record.get(key)
            if isinstance(value, list):
                for item in value:
                    tag = self._canonical_tag_value(item)
                    if tag:
                        tags.append(tag)
            elif isinstance(value, str) and value.strip():
                if "," in value:
                    for part in value.split(","):
                        tag = self._canonical_tag_value(part)
                        if tag:
                            tags.append(tag)
                else:
                    tag = self._canonical_tag_value(value)
                    if tag:
                        tags.append(tag)
        return self._dedupe_tags(tags)

    def _dedupe_tags(self, tags: List[str]) -> List[str]:
        unique: List[str] = []
        seen: set[str] = set()
        for tag in tags:
            cleaned = re.sub(r"\s+", " ", str(tag).strip())
            if not cleaned or len(cleaned) < 2:
                continue
            key = cleaned.lower()
            if key in seen or key in TAG_JUNK:
                continue
            seen.add(key)
            unique.append(cleaned[:50])
        return unique[:13]

    def _build_tag_index(self, raw_content: str) -> dict[str, List[str]]:
        index: dict[str, List[str]] = {}

        def store(key: str, tags: List[str]) -> None:
            if key and tags:
                index[key] = self._dedupe_tags([*index.get(key, []), *tags])

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                tags = self._tags_from_record(node)
                if not tags:
                    for value in node.values():
                        walk(value)
                    return
                listing_id = node.get("listing_id") or node.get("listingId")
                url = str(node.get("url") or node.get("listing_url") or node.get("product_url") or "")
                if listing_id is not None:
                    store(str(listing_id), tags)
                url_key = self._listing_key(url)
                if url_key:
                    store(url_key, tags)
                return
            if isinstance(node, list):
                for item in node:
                    walk(item)

        stripped = raw_content.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            payload = self._load_json(stripped)
            if payload is not None:
                walk(payload)

        soup = BeautifulSoup(raw_content, "lxml")
        for script in soup.find_all("script"):
            text = html.unescape(script.string or script.get_text() or "").strip()
            if not text.startswith(("{", "[")):
                continue
            payload = self._load_json(text)
            if payload is not None:
                walk(payload)

        for card in soup.select("[data-listing-id], [data-palette-listing-id]"):
            listing_id = card.get("data-listing-id") or card.get("data-palette-listing-id")
            if not listing_id:
                continue
            href_tags: List[str] = []
            for link in card.select("a.wt-tag, a[href*='/market/'], a[href*='tags='], a[href*='tag=']"):
                tag = self._tag_from_link_href(link.get("href", ""))
                if tag:
                    href_tags.append(tag)
            if href_tags:
                store(str(listing_id), href_tags)

        return index

    def is_valid_listing(self, listing: ProductListingSchema) -> bool:
        if not self._listing_key(listing.url):
            return False
        title = re.sub(r"\s+", " ", (listing.title or "").strip())
        if len(title) < MIN_TITLE_LENGTH:
            return False
        if JUNK_TITLE_RE.search(title):
            return False
        if title.lower() in {"etsy listing", "listing", "artículo de etsy", "articulo de etsy"}:
            return False
        lowered = title.lower()
        if any(
            phrase in lowered
            for phrase in (
                "añadir al carrito",
                "agregar al carrito",
                "añadir a favoritos",
                "add to favorites",
                "add to favourites",
                "iniciar sesión",
                "ver más",
                "envío gratis",
            )
        ):
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
        tags = self._tags_from_record(record)

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

        card_root = card or self._card_root(link)
        scope = card_root or link

        title_el = scope.select_one(
            "h3, h2, [data-listing-card-title], .v2-listing-card__title, .wt-text-caption"
        )
        title = ""
        if title_el and (card_root is not None or title_el.find_parent("a") is link):
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
            if not shop_name:
                shop_link = scope.select_one('a[href*="/shop/"]')
                if shop_link:
                    match = re.search(r"/shop/([^/?#]+)", shop_link.get("href", ""), re.I)
                    if match:
                        shop_name = match.group(1)
            if not shop_name:
                shop_name = scope.get("data-shop-name", "") if hasattr(scope, "get") else ""

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
