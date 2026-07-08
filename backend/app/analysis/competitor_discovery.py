"""Competitor query generation and marketplace search discovery."""

import re
from collections import Counter
from typing import Callable, List, Optional, Set

from app.analysis.keywords import STOPWORDS, _tokenize
from app.schemas import ProductListingSchema

STYLE_TERMS = {
    "minimalist", "modern", "abstract", "vintage", "rustic", "bohemian", "scandinavian",
    "neutral", "geometric", "botanical", "line", "beige", "black", "white", "boho",
}
PRODUCT_TERMS = {
    "print", "poster", "canvas", "art", "wall", "decor", "frame", "painting", "drawing",
    "illustration", "photography", "portrait", "landscape", "digital", "handmade",
}
USE_CASE_TERMS = {
    "bedroom", "living", "office", "nursery", "kitchen", "bathroom", "gift", "wedding",
    "home", "apartment", "studio",
}


def _shop_key(name: str) -> str:
    return re.sub(r"[\s_\-]+", "", (name or "").lower())


def is_own_shop(shop_name: str, user_shop_keys: Set[str]) -> bool:
    key = _shop_key(shop_name)
    return bool(key) and key in user_shop_keys


def extract_user_keywords(listings: List[ProductListingSchema]) -> Counter:
    counts: Counter = Counter()
    for listing in listings:
        counts.update(_tokenize(listing.title))
        counts.update(_tokenize(listing.description))
        for tag in listing.tags:
            counts.update(_tokenize(tag))
        for keyword in listing.detected_keywords:
            token = keyword.lower().strip()
            if token and token not in STOPWORDS:
                counts[token] += 1
        category = (listing.raw_data or {}).get("category", "")
        if category:
            counts.update(_tokenize(str(category)))
    return counts


def generate_competitor_queries(
    user_listings: List[ProductListingSchema],
    shop_name: str = "",
) -> List[str]:
    """Build marketplace search queries from the user's catalog themes."""
    keyword_counts = extract_user_keywords(user_listings)
    queries: List[str] = []
    seen: Set[str] = set()

    def add_query(query: str) -> None:
        normalized = re.sub(r"\s+", " ", query.strip().lower())
        if len(normalized) < 4 or normalized in seen:
            return
        seen.add(normalized)
        queries.append(query.strip())

    top_keywords = [word for word, _ in keyword_counts.most_common(12)]
    style_hits = [word for word in top_keywords if word in STYLE_TERMS]
    product_hits = [word for word in top_keywords if word in PRODUCT_TERMS]
    use_case_hits = [word for word in top_keywords if word in USE_CASE_TERMS]

    if len(top_keywords) >= 3:
        add_query(" ".join(top_keywords[:4]))
    if len(top_keywords) >= 2:
        add_query(" ".join(top_keywords[:2]))

    if style_hits and product_hits:
        add_query(f"{' '.join(style_hits[:2])} {' '.join(product_hits[:2])}")
    elif style_hits:
        add_query(" ".join(style_hits[:3]))
    elif product_hits:
        add_query(" ".join(product_hits[:3]))

    if use_case_hits and product_hits:
        add_query(f"{' '.join(use_case_hits[:1])} {' '.join(product_hits[:2])}")

    prices = [listing.price for listing in user_listings if listing.price > 0]
    if prices and top_keywords:
        avg_price = sum(prices) / len(prices)
        if avg_price <= 25:
            band = "affordable"
        elif avg_price <= 45:
            band = "mid range"
        else:
            band = "premium"
        add_query(f"{band} {' '.join(top_keywords[:2])}")

    for listing in user_listings[:5]:
        title_words = [word for word in _tokenize(listing.title) if word not in STOPWORDS]
        if len(title_words) >= 3:
            add_query(" ".join(title_words[:5]))

    return queries[:8]
