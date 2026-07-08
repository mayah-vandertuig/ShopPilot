"""Keyword analysis module."""

import re
from collections import Counter
from typing import Dict, List, Optional

from app.analysis.tag_intelligence import analyze_tag_intelligence
from app.schemas import KeywordSummary, ProductListingSchema

STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "your", "you", "are",
    "was", "has", "have", "will", "can", "all", "our", "not", "but", "into",
    "print", "art", "wall", "home", "decor", "gift", "gifts", "shop", "etsy",
}

CLUSTER_PATTERNS: Dict[str, List[str]] = {
    "Style": ["minimalist", "abstract", "scandinavian", "geometric", "line art", "botanical", "neutral", "vintage", "boho", "modern"],
    "Product type": ["canvas", "poster", "print", "framed", "set", "bundle", "digital", "wall art", "drawing"],
    "Room/use case": ["living room", "bedroom", "office", "nursery", "entryway", "gallery wall", "wedding", "gift"],
    "Theme": ["beige", "black", "white", "sage", "terracotta", "neutral", "handmade", "botanical"],
}


def extract_keywords(
    listings: List[ProductListingSchema],
    competitor_listings: Optional[List[ProductListingSchema]] = None,
) -> KeywordSummary:
    title_words: Counter = Counter()
    tag_words: Counter = Counter()
    competitor_title_words: Counter = Counter()
    competitor_tag_words: Counter = Counter()

    for listing in listings:
        words = _tokenize(listing.title)
        title_words.update(words)
        for tag in listing.tags:
            tag_words.update(_tokenize(tag))

    if competitor_listings:
        for listing in competitor_listings:
            competitor_title_words.update(_tokenize(listing.title))
            for tag in listing.tags:
                competitor_tag_words.update(_tokenize(tag))

    top_keywords = [{"keyword": keyword, "count": count} for keyword, count in title_words.most_common(15)]
    common_tags = [{"tag": tag, "count": count} for tag, count in tag_words.most_common(10)]
    competitor_keywords = [
        {"keyword": keyword, "count": count}
        for keyword, count in (competitor_title_words + competitor_tag_words).most_common(15)
    ]

    missing: List[str] = []
    if competitor_listings:
        shop_words = set(title_words.keys()) | set(tag_words.keys())
        competitor_words = competitor_title_words + competitor_tag_words
        missing = [
            keyword
            for keyword, count in competitor_words.most_common(30)
            if keyword not in shop_words and count >= 2
        ][:8]

    text_blob = " ".join(
        f"{listing.title} {' '.join(listing.tags)}" for listing in listings + (competitor_listings or [])
    ).lower()
    keyword_clusters = _build_clusters(text_blob)
    suggested_actions = _suggested_actions(top_keywords, missing, keyword_clusters)

    intelligence = analyze_tag_intelligence(listings, competitor_listings)
    intel_clusters = intelligence.get("keyword_clusters") or keyword_clusters
    intel_missing = [
        item["tag"] for item in intelligence.get("missing_tag_opportunities", [])[:8]
    ] or missing
    intel_actions = _intelligence_actions(intelligence) or suggested_actions

    return KeywordSummary(
        top_keywords=top_keywords,
        common_tags=common_tags,
        missing_opportunities=intel_missing,
        competitor_keywords=competitor_keywords,
        keyword_clusters=intel_clusters,
        suggested_actions=intel_actions,
        tag_insights=intelligence.get("tag_insights", []),
        summary_stats=intelligence.get("summary_stats", {}),
        missing_tag_opportunities=intelligence.get("missing_tag_opportunities", []),
        long_tail_opportunities=intelligence.get("long_tail_opportunities", []),
        tag_gap_analysis=intelligence.get("tag_gap_analysis", {}),
    )


def _build_clusters(text_blob: str) -> List[Dict[str, object]]:
    clusters = []
    for cluster_name, patterns in CLUSTER_PATTERNS.items():
        matches = [pattern for pattern in patterns if pattern in text_blob]
        if matches:
            clusters.append({"name": cluster_name, "keywords": matches[:6]})
    return clusters


def _intelligence_actions(intelligence: Dict[str, object]) -> List[str]:
    actions: List[str] = []
    stats = intelligence.get("summary_stats") or {}
    if stats.get("top_opportunity_tag"):
        actions.append(
            f"Prioritize '{stats['top_opportunity_tag']}' — highest opportunity score in your niche."
        )
    for item in (intelligence.get("missing_tag_opportunities") or [])[:2]:
        actions.append(
            f"Add '{item['tag']}' — used by {item['competitor_usage_count']} competitor listings."
        )
    for item in (intelligence.get("long_tail_opportunities") or [])[:1]:
        actions.append(f"Test long-tail tag '{item['tag']}' for easier ranking potential.")
    gap = intelligence.get("tag_gap_analysis") or {}
    if gap.get("weak_generic_tags"):
        actions.append(
            f"Replace generic tags like '{gap['weak_generic_tags'][0]}' with more specific long-tail phrases."
        )
    actions.append("Use all 13 Etsy tags; pair broad terms with specific buyer-intent phrases.")
    return actions[:5]


def _suggested_actions(
    top_keywords: List[Dict[str, object]],
    missing: List[str],
    clusters: List[Dict[str, object]],
) -> List[str]:
    actions: List[str] = []
    if top_keywords:
        lead = str(top_keywords[0]["keyword"])
        actions.append(f"Lead titles with '{lead}' — it appears most often in your catalog.")
    if missing:
        actions.append(f"Add missing tags like '{missing[0]}' used by similar competitor listings.")
    if clusters:
        cluster_keywords = clusters[0].get("keywords", [])
        if cluster_keywords:
            actions.append(
                f"Group listings around the {clusters[0]['name']} cluster: {', '.join(cluster_keywords[:3])}."
            )
    actions.append("Mirror high-performing competitor phrasing in the first 40 characters of titles.")
    actions.append("Use all 13 Etsy tags; prioritize buyer-intent phrases over generic decor terms.")
    return actions[:5]


def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    return [word for word in words if word not in STOPWORDS]
