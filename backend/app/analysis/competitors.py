"""Competitor analysis module."""

import json
import logging
import math
import re
from collections import Counter
from typing import Dict, List, Optional, Set

from app.analysis.competitor_discovery import extract_user_keywords
from app.analysis.keywords import STOPWORDS, _tokenize
from app.schemas import ProductListingSchema

logger = logging.getLogger(__name__)

COMPETITOR_LISTING_SOURCES = {"competitor", "competitor_search"}
USER_LISTING_SOURCES = {"user", "user_shop"}

DISCOVERED_LABEL = (
    "Discovered competitor — similar shop found from marketplace search results, "
    "not an official marketplace designation."
)


def _listing_source(listing: ProductListingSchema) -> str:
    source = (listing.listing_source or "").strip()
    if source:
        return source
    return str((listing.raw_data or {}).get("listing_source", "")).strip()


def _is_competitor_search_listing(listing: ProductListingSchema) -> bool:
    source = _listing_source(listing)
    if not source:
        return True
    if source in USER_LISTING_SOURCES:
        return False
    return source in COMPETITOR_LISTING_SOURCES


def _shop_key(name: str) -> str:
    return re.sub(r"[\s_\-]+", "", (name or "").lower())


def _pick_display_name(current: str, candidate: str) -> str:
    current = (current or "").strip()
    candidate = (candidate or "").strip()
    if not current:
        return candidate
    if not candidate:
        return current
    # Prefer Etsy-style shop slugs (no spaces) over title-cased display labels.
    if " " in current and " " not in candidate:
        return candidate
    if len(candidate) > len(current):
        return candidate
    return current


def _top_shop_keywords(listings: List[ProductListingSchema], token_counts: Counter) -> List[str]:
    tag_counts: Counter = Counter()
    for listing in listings:
        for tag in listing.tags:
            cleaned = re.sub(r"\s+", " ", str(tag).strip())
            if len(cleaned) >= 3:
                tag_counts[cleaned.lower()] += 1
    if tag_counts:
        return [tag for tag, _ in tag_counts.most_common(6)]

    words = [
        word
        for word, _ in token_counts.most_common(12)
        if len(word) >= 4 and word not in STOPWORDS
    ]
    return words[:6]


def _price_similarity(user_avg: float, competitor_avg: float) -> float:
    if user_avg <= 0 or competitor_avg <= 0:
        return 0.5
    ratio = min(user_avg, competitor_avg) / max(user_avg, competitor_avg)
    return max(0.0, min(1.0, ratio))


def _keyword_overlap(user_keywords: Set[str], competitor_keywords: Counter) -> float:
    if not user_keywords or not competitor_keywords:
        return 0.0
    overlap = sum(competitor_keywords.get(word, 0) for word in user_keywords)
    total = sum(competitor_keywords.values()) or 1
    return min(1.0, overlap / total)


def _review_strength(total_reviews: int, average_rating: float) -> float:
    review_score = min(1.0, math.log1p(total_reviews) / math.log1p(500))
    rating_score = average_rating / 5.0 if average_rating > 0 else 0.4
    return (review_score * 0.7) + (rating_score * 0.3)


def _position_score(positions: List[int]) -> float:
    if not positions:
        return 0.0
    bonuses = [max(0.0, 1.0 - (pos / 20.0)) for pos in positions]
    return sum(bonuses) / len(bonuses)


def compute_match_score(
    user_keywords: Set[str],
    user_avg_price: float,
    product_count: int,
    query_hits: int,
    total_reviews: int,
    average_rating: float,
    keyword_overlap_ratio: float,
    price_similarity: float,
    position_score: float,
) -> float:
    score = 0.0
    score += keyword_overlap_ratio * 40
    score += min(20.0, product_count * 4)
    score += min(15.0, query_hits * 5)
    score += _review_strength(total_reviews, average_rating) * 10
    score += price_similarity * 10
    score += position_score * 5
    return round(min(100.0, score), 1)


def _build_positioning_summary(
    match_score: float,
    common_keywords: List[str],
    average_price: float,
    user_avg_price: float,
    matched_queries: List[str],
) -> str:
    keyword_hint = ", ".join(common_keywords[:3]) if common_keywords else "similar product themes"
    price_hint = "similar pricing"
    if user_avg_price > 0 and average_price > 0:
        if average_price > user_avg_price * 1.15:
            price_hint = "higher average pricing"
        elif average_price < user_avg_price * 0.85:
            price_hint = "lower average pricing"

    query_hint = matched_queries[0] if matched_queries else "marketplace search"
    return (
        f"Discovered competitor with {match_score:.0f}/100 match score. "
        f"Found via searches like \"{query_hint}\" with overlap on {keyword_hint} and {price_hint}. "
        f"{DISCOVERED_LABEL}"
    )


def analyze_competitors(
    listings: List[ProductListingSchema],
    analysis_id: int,
    platform: str,
    user_listings: Optional[List[ProductListingSchema]] = None,
    exclude_shop_keys: Optional[Set[str]] = None,
) -> List[dict]:
    user_listings = user_listings or []
    exclude_shop_keys = exclude_shop_keys or set()

    user_keyword_counts = extract_user_keywords(user_listings)
    user_keywords = set(user_keyword_counts.keys())
    user_prices = [listing.price for listing in user_listings if listing.price > 0]
    user_avg_price = sum(user_prices) / len(user_prices) if user_prices else 0.0

    shops: Dict[str, dict] = {}

    for listing in listings:
        if not _is_competitor_search_listing(listing):
            continue
        shop = (listing.shop_name or "").strip()
        shop_key = _shop_key(shop)
        if not shop_key or shop_key in exclude_shop_keys:
            continue
        if shop.lower() in {"unknown shop", "etsy", "sample shop"}:
            continue

        if shop_key not in shops:
            shops[shop_key] = {
                "display_name": shop,
                "listings": [],
                "prices": [],
                "reviews": 0,
                "ratings": [],
                "keywords": Counter(),
                "matched_queries": Counter(),
                "positions": [],
                "urls": [],
                "titles": [],
                "platform": platform,
            }

        bucket = shops[shop_key]
        bucket["display_name"] = _pick_display_name(bucket["display_name"], shop)
        bucket["listings"].append(listing)
        bucket["prices"].append(listing.price)
        bucket["reviews"] += listing.review_count
        if listing.rating > 0:
            bucket["ratings"].append(listing.rating)
        bucket["keywords"].update(_tokenize(listing.title))
        bucket["keywords"].update(_tokenize(listing.description))
        for tag in listing.tags:
            bucket["keywords"].update(_tokenize(tag))

        raw = listing.raw_data or {}
        matched_query = raw.get("matched_query") or raw.get("competitor_query")
        if matched_query:
            bucket["matched_queries"][matched_query] += 1
        position = raw.get("search_position")
        if isinstance(position, int):
            bucket["positions"].append(position)

        if listing.url:
            bucket["urls"].append(listing.url)
        if listing.title:
            bucket["titles"].append(listing.title)
        bucket["platform"] = listing.platform or platform

    competitors = []
    for shop_key, data in shops.items():
        name = data["display_name"]
        prices = [price for price in data["prices"] if price > 0]
        avg_price = sum(prices) / len(prices) if prices else 0.0
        ratings = data["ratings"]
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        common_kw = _top_shop_keywords(data["listings"], data["keywords"])
        matched_queries = [query for query, _ in data["matched_queries"].most_common(5)]
        keyword_overlap_ratio = _keyword_overlap(user_keywords, data["keywords"])
        price_similarity = _price_similarity(user_avg_price, avg_price)
        position_score = _position_score(data["positions"])
        query_hits = len(data["matched_queries"])

        match_score = compute_match_score(
            user_keywords=user_keywords,
            user_avg_price=user_avg_price,
            product_count=len(data["listings"]),
            query_hits=query_hits,
            total_reviews=data["reviews"],
            average_rating=average_rating,
            keyword_overlap_ratio=keyword_overlap_ratio,
            price_similarity=price_similarity,
            position_score=position_score,
        )

        competitors.append({
            "analysis_id": analysis_id,
            "competitor_name": name,
            "platform": data["platform"],
            "product_count": len(data["listings"]),
            "average_price": round(avg_price, 2),
            "total_reviews": data["reviews"],
            "average_rating": round(average_rating, 2),
            "common_keywords": common_kw[:8],
            "matched_queries": matched_queries,
            "example_listing_urls": data["urls"][:5],
            "example_listing_titles": data["titles"][:5],
            "match_score": match_score,
            "positioning_summary": _build_positioning_summary(
                match_score,
                common_kw,
                avg_price,
                user_avg_price,
                matched_queries,
            ),
        })

    competitors.sort(
        key=lambda item: (item["match_score"], item["product_count"], item["total_reviews"]),
        reverse=True,
    )
    return competitors


def build_competitor_detail(
    competitor: dict,
    user_listings: List[ProductListingSchema],
    competitor_listings: List[ProductListingSchema],
) -> dict:
    shop_name = competitor["competitor_name"]
    shop_key = _shop_key(shop_name)
    own_listings = [
        listing for listing in competitor_listings
        if _shop_key(listing.shop_name) == shop_key
    ]

    user_keywords = set(extract_user_keywords(user_listings).keys())
    competitor_keywords = Counter()
    for listing in own_listings:
        competitor_keywords.update(_tokenize(listing.title))
        for tag in listing.tags:
            competitor_keywords.update(_tokenize(tag))

    overlap = sorted(user_keywords & set(competitor_keywords.keys()))
    user_only = sorted(user_keywords - set(competitor_keywords.keys()))[:8]
    competitor_only = sorted(set(competitor_keywords.keys()) - user_keywords)[:8]

    user_prices = [listing.price for listing in user_listings if listing.price > 0]
    comp_prices = [listing.price for listing in own_listings if listing.price > 0]
    user_avg = sum(user_prices) / len(user_prices) if user_prices else 0.0
    comp_avg = sum(comp_prices) / len(comp_prices) if comp_prices else competitor.get("average_price", 0.0)

    opportunities = []
    if user_only:
        opportunities.append(f"Lean into differentiators your shop already uses: {', '.join(user_only[:4])}.")
    if competitor_only:
        opportunities.append(
            f"Competitor emphasizes keywords you could test: {', '.join(competitor_only[:4])}."
        )
    if comp_avg > user_avg > 0:
        opportunities.append("This shop prices higher on average — room to emphasize value or premium materials.")
    elif user_avg > comp_avg > 0:
        opportunities.append("This shop prices lower on average — highlight quality, reviews, or bundles.")

    return {
        **competitor,
        "discovered_label": DISCOVERED_LABEL,
        "competing_listings": [
            {
                "title": listing.title,
                "url": listing.url,
                "price": listing.price,
                "rating": listing.rating,
                "review_count": listing.review_count,
                "image_url": listing.image_url,
            }
            for listing in own_listings[:12]
        ],
        "price_comparison": {
            "user_average_price": round(user_avg, 2),
            "competitor_average_price": round(comp_avg, 2),
            "delta": round(comp_avg - user_avg, 2),
        },
        "keyword_overlap": overlap[:12],
        "user_unique_keywords": user_only,
        "competitor_unique_keywords": competitor_only,
        "product_gaps": competitor_only[:6],
        "differentiation_opportunities": opportunities,
    }
