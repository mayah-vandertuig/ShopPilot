"""Trend detection module."""

from collections import Counter
from typing import Dict, List

from app.schemas import ProductListingSchema

TREND_PATTERNS = {
  "styles": ["minimalist", "abstract", "scandinavian", "geometric", "line art", "botanical", "neutral"],
  "materials": ["canvas", "paper", "wood", "metal", "linen", "framed"],
  "colors": ["beige", "black", "white", "sage", "terracotta", "neutral", "earth tone"],
  "use_cases": ["living room", "bedroom", "office", "gallery wall", "nursery", "entryway"],
}


def detect_trends(listings: List[ProductListingSchema], analysis_id: int) -> List[Dict]:
  text_blob = " ".join(
    f"{l.title} {l.description} {' '.join(l.tags)}" for l in listings
  ).lower()

  trends = []
  for trend_type, patterns in TREND_PATTERNS.items():
    counts = Counter()
    for pattern in patterns:
      count = text_blob.count(pattern)
      if count > 0:
        counts[pattern] = count

    for name, count in counts.most_common(3):
      if count >= 2:
        trends.append({
          "analysis_id": analysis_id,
          "trend_name": name.title(),
          "trend_type": trend_type.rstrip("s"),
          "evidence": f"Appears in {count} listing references across the dataset.",
          "opportunity": _opportunity_for(trend_type, name),
        })

  return trends[:12]


def _opportunity_for(trend_type: str, name: str) -> str:
  opportunities = {
    "styles": f"Create variations in the {name} style with differentiated color palettes.",
    "materials": f"Offer {name} options at multiple price points to capture budget and premium buyers.",
    "colors": f"Build a {name} collection for buyers seeking cohesive gallery walls.",
    "use_cases": f"Target {name} shoppers with room-specific sizing and staging imagery.",
  }
  return opportunities.get(trend_type, f"Explore product ideas around {name}.")
