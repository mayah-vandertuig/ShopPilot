"""Keyword analysis module."""

import re
from collections import Counter
from typing import Any, Dict, List

from app.schemas import KeywordSummary, ProductListingSchema

STOPWORDS = {
  "the", "and", "for", "with", "this", "that", "from", "your", "you", "are",
  "was", "has", "have", "will", "can", "all", "our", "not", "but", "into",
  "print", "art", "wall", "home", "decor",
}


def extract_keywords(listings: List[ProductListingSchema]) -> KeywordSummary:
  title_words: Counter = Counter()
  tag_words: Counter = Counter()

  for listing in listings:
    words = _tokenize(listing.title)
    title_words.update(words)
    for tag in listing.tags:
      tag_words.update(_tokenize(tag))

  top_keywords = [{"keyword": k, "count": v} for k, v in title_words.most_common(15)]
  common_tags = [{"tag": k, "count": v} for k, v in tag_words.most_common(10)]

  all_keywords = set(title_words.keys()) | set(tag_words.keys())
  niche_keywords = {"minimalist", "abstract", "line", "neutral", "beige", "scandinavian", "botanical", "geometric"}
  missing = sorted(niche_keywords - all_keywords)

  return KeywordSummary(
    top_keywords=top_keywords,
    common_tags=common_tags,
    missing_opportunities=missing[:8],
  )


def _tokenize(text: str) -> List[str]:
  words = re.findall(r"[a-zA-Z]{3,}", text.lower())
  return [w for w in words if w not in STOPWORDS]
