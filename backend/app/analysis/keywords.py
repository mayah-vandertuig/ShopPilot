"""Keyword analysis module."""

import re
from collections import Counter
from typing import List, Optional

from app.schemas import KeywordSummary, ProductListingSchema

STOPWORDS = {
    "the", "and", "for", "with", "this", "that", "from", "your", "you", "are",
    "was", "has", "have", "will", "can", "all", "our", "not", "but", "into",
    "print", "art", "wall", "home", "decor", "gift", "gifts", "shop", "etsy",
}


def extract_keywords(
    listings: List[ProductListingSchema],
    competitor_listings: Optional[List[ProductListingSchema]] = None,
) -> KeywordSummary:
    title_words: Counter = Counter()
    tag_words: Counter = Counter()

    for listing in listings:
        words = _tokenize(listing.title)
        title_words.update(words)
        for tag in listing.tags:
            tag_words.update(_tokenize(tag))

    top_keywords = [{"keyword": k, "count": v} for k, v in title_words.most_common(15)]
    common_tags = [{"tag": k, "count": v} for k, v in tag_words.most_common(10)]

    missing: List[str] = []
    if competitor_listings:
        shop_words = set(title_words.keys()) | set(tag_words.keys())
        competitor_words: Counter = Counter()
        for listing in competitor_listings:
            competitor_words.update(_tokenize(listing.title))
            for tag in listing.tags:
                competitor_words.update(_tokenize(tag))
        missing = [
            keyword
            for keyword, count in competitor_words.most_common(30)
            if keyword not in shop_words and count >= 2
        ][:8]

    return KeywordSummary(
        top_keywords=top_keywords,
        common_tags=common_tags,
        missing_opportunities=missing,
    )


def _tokenize(text: str) -> List[str]:
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    return [w for w in words if w not in STOPWORDS]
