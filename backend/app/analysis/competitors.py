"""Competitor analysis module."""

from collections import defaultdict
from typing import List

from app.analysis.keywords import _tokenize
from app.schemas import CompetitorRead, ProductListingSchema


def analyze_competitors(listings: List[ProductListingSchema], analysis_id: int, platform: str) -> List[dict]:
  shops: dict = defaultdict(lambda: {"prices": [], "reviews": 0, "keywords": []})

  for listing in listings:
    shop = listing.shop_name or "Unknown Shop"
    shops[shop]["prices"].append(listing.price)
    shops[shop]["reviews"] += listing.review_count
    shops[shop]["keywords"].extend(_tokenize(listing.title))
    shops[shop]["platform"] = listing.platform

  competitors = []
  for name, data in shops.items():
    prices = [p for p in data["prices"] if p > 0]
    avg_price = sum(prices) / len(prices) if prices else 0
    kw_counts: dict = {}
    for k in data["keywords"]:
      kw_counts[k] = kw_counts.get(k, 0) + 1
    common_kw = sorted(kw_counts, key=kw_counts.get, reverse=True)[:5]

    if avg_price > 40:
      positioning = "Premium positioning with higher average prices"
    elif avg_price > 25:
      positioning = "Mid-market competitor with balanced pricing"
    else:
      positioning = "Budget-friendly competitor with volume focus"

    competitors.append({
      "analysis_id": analysis_id,
      "competitor_name": name,
      "platform": platform,
      "product_count": len(data["prices"]),
      "average_price": round(avg_price, 2),
      "total_reviews": data["reviews"],
      "common_keywords": common_kw,
      "positioning_summary": positioning,
    })

  competitors.sort(key=lambda c: (c["product_count"], c["total_reviews"]), reverse=True)
  return competitors
