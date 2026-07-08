"""Content locale detection for marketplace scraping."""

import logging
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

