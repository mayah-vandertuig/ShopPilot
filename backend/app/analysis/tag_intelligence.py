"""Tag and keyword intelligence analysis for Etsy sellers."""

import re
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Set, Tuple

from app.schemas import KeywordInsight, ProductListingSchema

KEYWORD_TYPES = ("style", "product", "room", "theme", "format", "seasonal", "audience")

TYPE_PATTERNS: Dict[str, List[str]] = {
    "style": [
        "minimalist", "abstract", "modern", "neutral", "vintage", "boho", "scandinavian",
        "geometric", "contemporary", "rustic", "industrial", "mid century", "bauhaus",
    ],
    "product": [
        "wall art", "poster", "printable", "art print", "gallery wall", "canvas",
        "drawing", "illustration", "poster set", "print set",
    ],
    "room": [
        "kitchen", "bedroom", "nursery", "office", "living room", "bathroom", "entryway",
        "dining room", "hallway",
    ],
    "theme": [
        "botanical", "citrus", "coastal", "bauhaus", "geometric", "landscape",
        "floral", "nature", "beach", "mountain", "forest", "abstract",
    ],
    "format": [
        "digital download", "printable", "poster set", "gallery wall set",
        "instant download", "pdf download", "printable wall art",
    ],
    "seasonal": [
        "christmas", "halloween", "spring", "summer", "fall", "winter", "holiday",
        "valentine", "easter",
    ],
    "audience": [
        "nursery", "kids", "baby", "wedding", "gift", "housewarming", "new home",
    ],
}

CLUSTER_GROUPS: Dict[str, List[str]] = {
    "Style": ["minimalist", "abstract", "modern", "neutral", "vintage"],
    "Product type": ["wall art", "poster", "printable", "art print", "gallery wall"],
    "Room/use case": ["kitchen", "bedroom", "nursery", "office", "living room"],
    "Theme": ["botanical", "citrus", "coastal", "bauhaus", "geometric"],
    "Format": ["digital download", "printable", "poster set", "gallery wall set", "instant download"],
}

GENERIC_TAGS = {
    "wall art", "home decor", "gift", "handmade", "print", "art", "decor",
    "home", "gifts", "etsy", "shop", "poster", "drawing", "canvas",
}

DEMAND_LABELS = ("Low", "Medium", "High")
COMPETITION_LABELS = ("Low", "Medium", "High")
ENGAGEMENT_LABELS = ("weak", "medium", "strong")


def _normalize_tag(tag: str) -> str:
    return re.sub(r"\s+", " ", tag.strip().lower())


def extract_tags_from_user_listings(listings: List[ProductListingSchema]) -> Counter:
    counts: Counter = Counter()
    for listing in listings:
        for tag in listing.tags:
            normalized = _normalize_tag(tag)
            if normalized and len(normalized) >= 3:
                counts[normalized] += 1
        for phrase in _extract_title_phrases(listing.title):
            counts[phrase] += 1
    return counts


def extract_tags_from_competitor_listings(
    listings: List[ProductListingSchema],
    search_queries: Optional[List[str]] = None,
) -> Counter:
    counts: Counter = Counter()
    for listing in listings:
        for tag in listing.tags:
            normalized = _normalize_tag(tag)
            if normalized and len(normalized) >= 3:
                counts[normalized] += 1
        for phrase in _extract_title_phrases(listing.title):
            counts[phrase] += 1
        if listing.description:
            for phrase in _extract_title_phrases(listing.description):
                counts[phrase] += 1
    if search_queries:
        for query in search_queries:
            normalized = _normalize_tag(query)
            if normalized:
                counts[normalized] += 2
    return counts


def _extract_title_phrases(text: str) -> List[str]:
    """Extract 2-4 word phrases from titles/descriptions."""
    words = re.findall(r"[a-zA-Z]+", text.lower())
    phrases: List[str] = []
    for size in (2, 3, 4):
        for i in range(len(words) - size + 1):
            chunk = words[i : i + size]
            if any(len(w) < 3 for w in chunk):
                continue
            phrase = " ".join(chunk)
            if phrase not in GENERIC_TAGS and not all(w in GENERIC_TAGS for w in chunk):
                phrases.append(phrase)
    return phrases


def classify_keyword_type(tag: str) -> str:
    tag_lower = tag.lower()
    # Room patterns take priority when the tag starts with or centers on a room
    room_patterns = TYPE_PATTERNS["room"]
    for pattern in room_patterns:
        if tag_lower.startswith(pattern) or f" {pattern}" in f" {tag_lower}":
            return "room"
    best_type = "theme"
    best_score = 0
    for keyword_type, patterns in TYPE_PATTERNS.items():
        if keyword_type == "room":
            continue
        score = sum(1 for pattern in patterns if pattern in tag_lower or tag_lower in pattern)
        if score > best_score:
            best_score = score
            best_type = keyword_type
    return best_type


def calculate_tag_gap(
    user_counts: Counter,
    competitor_counts: Counter,
) -> Dict[str, List[str]]:
    user_tags = set(user_counts.keys())
    competitor_tags = set(competitor_counts.keys())

    user_frequent = [t for t, c in user_counts.most_common(15) if c >= 2]
    competitor_frequent = [t for t, c in competitor_counts.most_common(15) if c >= 2]
    shared = sorted(user_tags & competitor_tags, key=lambda t: competitor_counts[t], reverse=True)
    missing = [
        t for t, c in competitor_counts.most_common(30)
        if c >= 2 and (t not in user_tags or user_counts[t] < 2)
    ]
    weak_generic = [
        t for t, c in user_counts.most_common(20)
        if t in GENERIC_TAGS or (c >= 3 and len(t.split()) == 1)
    ]

    return {
        "user_frequent_tags": user_frequent[:10],
        "competitor_frequent_tags": competitor_frequent[:10],
        "shared_tags": shared[:10],
        "missing_tags": missing[:10],
        "weak_generic_tags": weak_generic[:8],
    }


def estimate_keyword_demand(
    tag: str,
    competitor_count: int,
    search_query_hits: int = 0,
) -> str:
    score = competitor_count + search_query_hits
    if score >= 8:
        return "High"
    if score >= 3:
        return "Medium"
    return "Low"


def estimate_keyword_competition(tag: str, competitor_count: int, total_competitors: int) -> str:
    word_count = len(tag.split())
    if tag in GENERIC_TAGS or word_count == 1:
        return "High"
    adoption = competitor_count / max(total_competitors, 1)
    # Long-tail tags need higher adoption to count as competitive
    if word_count >= 3:
        if adoption >= 0.5 or competitor_count >= 12:
            return "High"
        if adoption >= 0.35 or competitor_count >= 6:
            return "Medium"
        return "Low"
    if adoption >= 0.6 or competitor_count >= 15:
        return "High"
    if adoption >= 0.25 or competitor_count >= 5:
        return "Medium"
    return "Low"


def estimate_engagement(competitor_count: int, avg_reviews: float) -> str:
    if competitor_count >= 6 and avg_reviews >= 30:
        return "strong"
    if competitor_count >= 3 or avg_reviews >= 15:
        return "medium"
    return "weak"


def _long_tail_bonus(tag: str) -> float:
    words = tag.split()
    if len(words) >= 3:
        return 15.0
    if len(words) == 2:
        return 8.0
    return 0.0


def _trend_direction(tag: str, competitor_listings: List[ProductListingSchema]) -> str:
    positions = []
    for listing in competitor_listings:
        if tag in _normalize_tag(listing.title) or any(tag in _normalize_tag(t) for t in listing.tags):
            pos = listing.raw_data.get("search_position")
            if pos is not None:
                positions.append(int(pos))
    if len(positions) >= 3 and sum(positions) / len(positions) < 10:
        return "rising"
    if len(positions) >= 2:
        return "stable"
    return "stable"


def _trend_bonus(direction: str) -> float:
    return {"rising": 8.0, "stable": 2.0, "declining": -5.0}.get(direction, 0.0)


def _relevance_score(tag: str, user_counts: Counter) -> float:
    tag_words = set(tag.split())
    user_words: Set[str] = set()
    for user_tag in user_counts:
        user_words.update(user_tag.split())
    overlap = len(tag_words & user_words)
    if overlap >= 2:
        return 20.0
    if overlap == 1:
        return 12.0
    return 5.0


def calculate_opportunity_score(
    tag: str,
    competitor_count: int,
    user_count: int,
    demand: str,
    competition: str,
    trend_direction: str,
    user_counts: Counter,
) -> int:
    demand_score = {"High": 25, "Medium": 15, "Low": 5}.get(demand, 10)
    relevance = _relevance_score(tag, user_counts)
    competitor_validation = min(20.0, competitor_count * 2.5)
    gap_score = 0.0
    if competitor_count >= 2 and user_count == 0:
        gap_score = 20.0
    elif competitor_count >= 2 and user_count < 2:
        gap_score = 12.0
    elif user_count >= 3 and tag in GENERIC_TAGS:
        gap_score = -5.0
    long_tail = _long_tail_bonus(tag)
    trend = _trend_bonus(trend_direction)
    competition_penalty = {"High": 15, "Medium": 7, "Low": 0}.get(competition, 5)
    if tag in GENERIC_TAGS:
        competition_penalty += 10

    raw = (
        demand_score
        + relevance
        + competitor_validation
        + gap_score
        + long_tail
        + trend
        - competition_penalty
    )
    return max(0, min(100, int(round(raw))))


def _listings_for_tag(
    tag: str,
    listings: List[ProductListingSchema],
    limit: int = 3,
) -> List[Dict[str, object]]:
    results = []
    tag_lower = tag.lower()
    for listing in listings:
        haystack = f"{listing.title} {' '.join(listing.tags)}".lower()
        if tag_lower in haystack:
            results.append({
                "title": listing.title,
                "url": listing.url,
                "shop_name": listing.shop_name,
                "price": listing.price,
            })
        if len(results) >= limit:
            break
    return results


def _related_tags(tag: str, all_tags: List[str], limit: int = 5) -> List[str]:
    tag_words = set(tag.split())
    scored: List[Tuple[int, str]] = []
    for other in all_tags:
        if other == tag:
            continue
        other_words = set(other.split())
        overlap = len(tag_words & other_words)
        if overlap > 0:
            scored.append((overlap, other))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [t for _, t in scored[:limit]]


def _suggested_action(
    tag: str,
    keyword_type: str,
    user_count: int,
    competitor_count: int,
    opportunity_score: int,
    competition: str,
) -> str:
    if user_count == 0 and competitor_count >= 3:
        return f"Add to {keyword_type}-focused listings — competitors use this {competitor_count} times"
    if user_count == 0:
        return f"Test on new listings targeting {tag}"
    if tag in GENERIC_TAGS or competition == "High":
        return "Keep using, but pair with more specific long-tail tags"
    if opportunity_score >= 75:
        return f"Prioritize — strong opportunity for {keyword_type} listings"
    if user_count >= 3:
        return "Already well covered — focus on long-tail variations"
    return f"Add to relevant {keyword_type} listings"


def _pricing_context(tag: str, listings: List[ProductListingSchema]) -> Optional[str]:
    prices = []
    for listing in listings:
        haystack = f"{listing.title} {' '.join(listing.tags)}".lower()
        if tag in haystack and listing.price > 0:
            prices.append(listing.price)
    if len(prices) < 2:
        return None
    avg = sum(prices) / len(prices)
    return f"Listings using this tag average {avg:.2f} (based on competitor usage)"


def _search_query_hits(tag: str, queries: List[str]) -> int:
    tag_lower = tag.lower()
    return sum(1 for q in queries if tag_lower in q.lower() or q.lower() in tag_lower)


def build_keyword_insights(
    user_listings: List[ProductListingSchema],
    competitor_listings: List[ProductListingSchema],
    search_queries: Optional[List[str]] = None,
) -> List[KeywordInsight]:
    search_queries = search_queries or []
    user_counts = extract_tags_from_user_listings(user_listings)
    competitor_counts = extract_tags_from_competitor_listings(competitor_listings, search_queries)

    all_tags = set(user_counts.keys()) | set(competitor_counts.keys())
    unique_shops = len({l.shop_name for l in competitor_listings if l.shop_name})
    insights: List[KeywordInsight] = []

    for tag in all_tags:
        if len(tag) < 3:
            continue
        comp_count = competitor_counts.get(tag, 0)
        user_count = user_counts.get(tag, 0)
        if comp_count == 0 and user_count == 0:
            continue

        keyword_type = classify_keyword_type(tag)
        query_hits = _search_query_hits(tag, search_queries)
        demand = estimate_keyword_demand(tag, comp_count, query_hits)
        competition = estimate_keyword_competition(tag, comp_count, max(unique_shops, 1))

        comp_listings_with_tag = [
            l for l in competitor_listings
            if tag in f"{l.title} {' '.join(l.tags)}".lower()
        ]
        avg_reviews = (
            sum(l.review_count for l in comp_listings_with_tag) / len(comp_listings_with_tag)
            if comp_listings_with_tag else 0
        )
        engagement = estimate_engagement(comp_count, avg_reviews)
        trend = _trend_direction(tag, competitor_listings)
        score = calculate_opportunity_score(
            tag, comp_count, user_count, demand, competition, trend, user_counts
        )

        insights.append(KeywordInsight(
            tag=tag,
            keyword_type=keyword_type,
            competitor_usage_count=comp_count,
            user_usage_count=user_count,
            search_volume_estimate=demand,
            competition_estimate=competition,
            engagement_estimate=engagement,
            opportunity_score=score,
            trend_direction=trend,
            related_tags=_related_tags(tag, list(all_tags)),
            example_competitor_listings=_listings_for_tag(tag, competitor_listings),
            example_user_listings=_listings_for_tag(tag, user_listings),
            suggested_action=_suggested_action(tag, keyword_type, user_count, comp_count, score, competition),
            suggested_title_phrases=[f"{tag.title()} — {keyword_type} print"],
            suggested_etsy_tags=[tag[:20]],
            suggested_description_phrase=f"Features a {tag} design perfect for modern home styling.",
            pricing_context=_pricing_context(tag, competitor_listings),
        ))

    insights.sort(key=lambda i: (-i.opportunity_score, -i.competitor_usage_count))
    return insights


def generate_long_tail_opportunities(
    insights: List[KeywordInsight],
    competitor_listings: List[ProductListingSchema],
) -> List[Dict[str, object]]:
    long_tail = [i for i in insights if len(i.tag.split()) >= 2 and i.opportunity_score >= 40]
    long_tail.sort(key=lambda i: (-i.opportunity_score, -len(i.tag.split())))

    results = []
    for insight in long_tail[:12]:
        keyword_type = insight.keyword_type
        results.append({
            "tag": insight.tag,
            "estimated_demand": insight.search_volume_estimate,
            "estimated_competition": insight.competition_estimate,
            "opportunity_score": insight.opportunity_score,
            "recommended_listing_type": f"{keyword_type.title()} print",
            "suggested_title_phrase": insight.suggested_title_phrases[0] if insight.suggested_title_phrases else insight.tag.title(),
            "suggested_etsy_tag": insight.tag[:20],
        })

    if len(results) < 5:
        for listing in competitor_listings:
            for phrase in _extract_title_phrases(listing.title):
                if len(phrase.split()) >= 2 and phrase not in {r["tag"] for r in results}:
                    results.append({
                        "tag": phrase,
                        "estimated_demand": "Medium",
                        "estimated_competition": "Low",
                        "opportunity_score": 55,
                        "recommended_listing_type": "Wall art print",
                        "suggested_title_phrase": phrase.title(),
                        "suggested_etsy_tag": phrase[:20],
                    })
                if len(results) >= 8:
                    break
            if len(results) >= 8:
                break

    return results[:10]


def build_missing_tag_opportunities(insights: List[KeywordInsight]) -> List[Dict[str, object]]:
    missing = [
        i for i in insights
        if i.competitor_usage_count >= 2 and i.user_usage_count < 2
    ]
    missing.sort(key=lambda i: (-i.opportunity_score, -i.competitor_usage_count))

    results = []
    for insight in missing[:10]:
        why = (
            f"Used by {insight.competitor_usage_count} competitor listings with "
            f"{insight.search_volume_estimate.lower()} estimated demand"
        )
        suggested = [
            ex.get("title", "") for ex in insight.example_user_listings[:2]
        ] or [f"New {insight.keyword_type} listing"]
        results.append({
            "tag": insight.tag,
            "competitor_usage_count": insight.competitor_usage_count,
            "user_usage_count": insight.user_usage_count,
            "example_competitor_listings": insight.example_competitor_listings,
            "why_it_matters": why,
            "suggested_listings_to_add": suggested,
        })
    return results


def group_keywords_into_clusters(insights: List[KeywordInsight]) -> List[Dict[str, object]]:
    tag_set = {i.tag.lower() for i in insights}
    clusters = []
    for cluster_name, patterns in CLUSTER_GROUPS.items():
        matches = []
        for pattern in patterns:
            for tag in tag_set:
                if pattern in tag or tag in pattern:
                    if tag not in matches:
                        matches.append(tag)
        if matches:
            clusters.append({"name": cluster_name, "keywords": matches[:8]})
    return clusters


def build_summary_stats(
    insights: List[KeywordInsight],
    long_tail: List[Dict[str, object]],
    gap: Dict[str, List[str]],
) -> Dict[str, object]:
    top_opp = insights[0].tag if insights else ""
    highest_comp = max(insights, key=lambda i: i.competitor_usage_count).tag if insights else ""
    missing_count = len(gap.get("missing_tags", []))
    overused = len(gap.get("weak_generic_tags", []))

    return {
        "total_tags_analyzed": len(insights),
        "top_opportunity_tag": top_opp,
        "highest_competitor_tag": highest_comp,
        "missing_tags_count": missing_count,
        "overused_generic_count": overused,
        "long_tail_count": len(long_tail),
    }


def _collect_search_queries(competitor_listings: List[ProductListingSchema]) -> List[str]:
    queries: List[str] = []
    seen: Set[str] = set()
    for listing in competitor_listings:
        query = listing.raw_data.get("matched_query", "")
        if query and query not in seen:
            seen.add(query)
            queries.append(query)
    return queries


def analyze_tag_intelligence(
    user_listings: List[ProductListingSchema],
    competitor_listings: Optional[List[ProductListingSchema]] = None,
) -> Dict[str, object]:
    competitor_listings = competitor_listings or []
    search_queries = _collect_search_queries(competitor_listings)

    user_counts = extract_tags_from_user_listings(user_listings)
    competitor_counts = extract_tags_from_competitor_listings(competitor_listings, search_queries)
    gap = calculate_tag_gap(user_counts, competitor_counts)
    insights = build_keyword_insights(user_listings, competitor_listings, search_queries)
    long_tail = generate_long_tail_opportunities(insights, competitor_listings)
    missing = build_missing_tag_opportunities(insights)
    clusters = group_keywords_into_clusters(insights)
    stats = build_summary_stats(insights, long_tail, gap)

    return {
        "tag_insights": [i.model_dump() for i in insights],
        "summary_stats": stats,
        "missing_tag_opportunities": missing,
        "long_tail_opportunities": long_tail,
        "tag_gap_analysis": gap,
        "keyword_clusters": clusters,
    }
