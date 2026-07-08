"""Content locale detection and mock fallback for marketplace scraping."""

import logging
import re
from typing import List, Optional

from app.schemas import ProductListingSchema

logger = logging.getLogger(__name__)

SPANISH_MARKERS = (
    "añadir",
    "agregar",
    "carrito",
    "precio",
    "envío",
    "envio",
    "comprar",
    "favoritos",
    "iniciar sesión",
    "iniciar sesion",
    "resultados",
    "búsqueda",
    "busqueda",
    "artículo",
    "articulo",
    "ver más",
    "ver mas",
    "vendido",
    "español",
    "espanol",
    "tienda",
)

ENGLISH_MARKERS = (
    "add to cart",
    "search",
    "results",
    "shipping",
    "price",
    "buy it now",
    "shop now",
    "free shipping",
    "reviews",
)

LOCALE_MISMATCH_WARNING = (
    "Scraped content appears to be localized in Spanish. "
    "Check Bright Data geolocation, headers, cookies, or URL locale parameters."
)


def detect_unexpected_locale(content: str, requested_language: str) -> Optional[str]:
    """Return a warning when scraped content looks localized differently than requested."""
    if not content or not requested_language.lower().startswith("en"):
        return None

    lowered = content.lower()
    spanish_hits = sum(1 for marker in SPANISH_MARKERS if marker in lowered)
    english_hits = sum(1 for marker in ENGLISH_MARKERS if marker in lowered)

    if spanish_hits >= 3 and spanish_hits > english_hits:
        logger.warning(
            "Scraped content appears Spanish while %s was requested (spanish=%s, english=%s)",
            requested_language,
            spanish_hits,
            english_hits,
        )
        return LOCALE_MISMATCH_WARNING
    return None


def is_poor_parse_quality(listings: List[ProductListingSchema]) -> bool:
    if not listings:
        return True
    valid = [listing for listing in listings if listing.title and len(listing.title.strip()) >= 8]
    return len(valid) < max(1, len(listings) // 2)


def mock_listings_for_query(platform: str, query: str, currency: str = "USD") -> List[ProductListingSchema]:
    """Fallback sample listings when live parsing quality is poor."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", query.strip()).strip("-").lower() or "sample"
    titles = [
        f"{query.title()} Print",
        f"Minimal {query.title()} Poster",
        f"Handmade {query.title()} Art",
    ]
    listings: List[ProductListingSchema] = []
    for index, title in enumerate(titles, start=1):
        listings.append(
            ProductListingSchema(
                platform=platform,
                title=title,
                url=f"https://example.com/{platform}/{slug}/{index}",
                shop_name="Sample Shop",
                price=18.0 + index * 4,
                currency=currency,
                tags=[word.lower() for word in query.split() if len(word) > 3][:4],
                detected_keywords=[word.lower() for word in query.split() if len(word) > 3],
            )
        )
    return listings
