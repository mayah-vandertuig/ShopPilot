"""Trend detection module."""

from collections import Counter
from statistics import median
from typing import Dict, List, Set

from app.analysis.keywords import STOPWORDS, _tokenize
from app.schemas import ProductListingSchema

TREND_PATTERNS = {
    "style": ["minimalist", "abstract", "scandinavian", "geometric", "line art", "botanical", "neutral", "vintage", "boho"],
    "product_type": ["canvas", "poster", "print", "framed", "set", "bundle", "wall art"],
    "color": ["beige", "black", "white", "sage", "terracotta", "neutral", "gold", "silver"],
    "use_case": ["living room", "bedroom", "office", "gallery wall", "nursery", "entryway", "wedding", "gift"],
}


def detect_trends(listings: List[ProductListingSchema], analysis_id: int) -> List[Dict]:
    if not listings:
        return []

    text_blob = " ".join(
        f"{listing.title} {listing.description} {' '.join(listing.tags)}" for listing in listings
    ).lower()

    min_count = 1 if len(listings) < 8 else 2
    trends: List[Dict] = []
    seen_names: Set[str] = set()

    for trend_type, patterns in TREND_PATTERNS.items():
        counts = Counter()
        for pattern in patterns:
            count = text_blob.count(pattern)
            if count > 0:
                counts[pattern] = count

        for name, count in counts.most_common(3):
            key = name.lower()
            if count >= min_count and key not in seen_names:
                seen_names.add(key)
                examples = _matching_listings(listings, name)
                prices = [listing.price for listing in examples if listing.price > 0]
                trends.append(_build_trend(
                    analysis_id=analysis_id,
                    name=name,
                    trend_type=trend_type,
                    count=count,
                    total=len(listings),
                    examples=examples,
                    prices=prices,
                ))

    word_counts: Counter = Counter()
    for listing in listings:
        words = set(_tokenize(f"{listing.title} {' '.join(listing.tags)}"))
        for word in words:
            if len(word) >= 4 and word not in STOPWORDS:
                word_counts[word] += 1

    for word, count in word_counts.most_common(12):
        if count < min_count or word in seen_names:
            continue
        seen_names.add(word)
        examples = _matching_listings(listings, word)
        prices = [listing.price for listing in examples if listing.price > 0]
        trends.append(_build_trend(
            analysis_id=analysis_id,
            name=word,
            trend_type="keyword",
            count=count,
            total=len(listings),
            examples=examples,
            prices=prices,
        ))
        if len(trends) >= 12:
            break

    return trends[:12]


def _matching_listings(listings: List[ProductListingSchema], term: str) -> List[ProductListingSchema]:
    needle = term.lower()
    matches = []
    for listing in listings:
        haystack = f"{listing.title} {listing.description} {' '.join(listing.tags)}".lower()
        if needle in haystack:
            matches.append(listing)
    return matches[:4]


def _build_trend(
    *,
    analysis_id: int,
    name: str,
    trend_type: str,
    count: int,
    total: int,
    examples: List[ProductListingSchema],
    prices: List[float],
) -> Dict:
    confidence = min(0.95, 0.45 + (count / max(total, 1)) * 0.5)
    price_range = ""
    if prices:
        med = median(prices)
        price_range = f"${max(0, med * 0.85):.0f}–${med * 1.15:.0f}"

    competitor_examples = [
        {
            "title": listing.title,
            "shop_name": listing.shop_name,
            "price": listing.price,
            "url": listing.url,
        }
        for listing in examples[:3]
    ]

    return {
        "analysis_id": analysis_id,
        "trend_name": name.title(),
        "trend_type": trend_type,
        "evidence": f"Appears in {count} listing reference{'s' if count != 1 else ''} across {total} collected products.",
        "opportunity": _opportunity_for(trend_type, name),
        "details": {
            "competitor_examples": competitor_examples,
            "suggested_product_idea": _product_idea_for(trend_type, name),
            "keywords": [name.lower(), *_related_keywords(name, trend_type)],
            "price_range": price_range,
            "confidence": round(confidence, 2),
        },
    }


def _related_keywords(name: str, trend_type: str) -> List[str]:
    related = {
        "style": ["wall art", "home decor"],
        "product_type": ["handmade", "gift"],
        "color": ["neutral", "decor"],
        "use_case": ["interior", "gift idea"],
        "keyword": ["etsy", "print"],
    }
    return related.get(trend_type, [])[:2]


def _product_idea_for(trend_type: str, name: str) -> str:
    ideas = {
        "style": f"A coordinated {name} wall art set in two sizes for gallery walls.",
        "product_type": f"A premium {name} bundle with matching color palette options.",
        "color": f"A {name} mini-collection with framed and unframed variants.",
        "use_case": f"A {name}-focused listing with room-staging mockups and size guide.",
        "keyword": f"Expand listings that emphasize '{name}' with clearer buyer-intent titles.",
    }
    return ideas.get(trend_type, f"Explore a new listing line around {name}.")


def _opportunity_for(trend_type: str, name: str) -> str:
    opportunities = {
        "style": f"Create variations in the {name} style with differentiated color palettes.",
        "product_type": f"Offer {name} options at multiple price points to capture budget and premium buyers.",
        "color": f"Build a {name} collection for buyers seeking cohesive sets.",
        "use_case": f"Target {name} shoppers with room-specific sizing and staging imagery.",
        "keyword": f"Use '{name}' consistently across titles and tags to match buyer search intent.",
    }
    return opportunities.get(trend_type, f"Explore product ideas around {name}.")
