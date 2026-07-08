"""Trend detection module."""

from collections import Counter
from typing import Dict, List, Set

from app.analysis.keywords import STOPWORDS, _tokenize
from app.schemas import ProductListingSchema

TREND_PATTERNS = {
  "style": ["minimalist", "abstract", "scandinavian", "geometric", "line art", "botanical", "neutral", "vintage", "boho"],
  "material": ["canvas", "paper", "wood", "metal", "linen", "framed", "ceramic", "glass"],
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
        trends.append({
          "analysis_id": analysis_id,
          "trend_name": name.title(),
          "trend_type": trend_type,
          "evidence": f"Appears in {count} listing reference{'s' if count != 1 else ''} across the dataset.",
          "opportunity": _opportunity_for(trend_type, name),
        })

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
    trends.append({
      "analysis_id": analysis_id,
      "trend_name": word.title(),
      "trend_type": "keyword",
      "evidence": f"Found in {count} of {len(listings)} listing titles or tags.",
      "opportunity": f"Lean into '{word}' in titles, tags, and imagery where it fits your catalog.",
    })
    if len(trends) >= 12:
      break

  return trends[:12]


def _opportunity_for(trend_type: str, name: str) -> str:
  opportunities = {
    "style": f"Create variations in the {name} style with differentiated color palettes.",
    "material": f"Offer {name} options at multiple price points to capture budget and premium buyers.",
    "color": f"Build a {name} collection for buyers seeking cohesive sets.",
    "use_case": f"Target {name} shoppers with room-specific sizing and staging imagery.",
    "keyword": f"Use '{name}' consistently across titles and tags to match buyer search intent.",
  }
  return opportunities.get(trend_type, f"Explore product ideas around {name}.")
