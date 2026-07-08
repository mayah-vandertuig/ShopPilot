"""Pricing analysis module."""

from statistics import median
from typing import Any, Dict, List

from app.schemas import PricingSummary, ProductListingSchema


def calculate_pricing_summary(listings: List[ProductListingSchema]) -> PricingSummary:
  prices = [l.price for l in listings if l.price and l.price > 0]
  if not prices:
    return PricingSummary()

  avg = sum(prices) / len(prices)
  med = median(prices)
  min_p = min(prices)
  max_p = max(prices)
  suggested_min = round(med * 0.85, 2)
  suggested_max = round(med * 1.15, 2)

  underpriced = _find_outliers(listings, med * 0.7, below=True)
  overpriced = _find_outliers(listings, med * 1.4, below=False)

  return PricingSummary(
    min_price=round(min_p, 2),
    max_price=round(max_p, 2),
    average_price=round(avg, 2),
    median_price=round(med, 2),
    suggested_min=suggested_min,
    suggested_max=suggested_max,
    underpriced=underpriced,
    overpriced=overpriced,
  )


def _find_outliers(listings: List[ProductListingSchema], threshold: float, below: bool) -> List[Dict[str, Any]]:
  results = []
  for l in listings:
    if not l.price:
      continue
    if below and l.price < threshold:
      results.append({"title": l.title, "price": l.price, "shop_name": l.shop_name})
    elif not below and l.price > threshold:
      results.append({"title": l.title, "price": l.price, "shop_name": l.shop_name})
  return results[:5]
