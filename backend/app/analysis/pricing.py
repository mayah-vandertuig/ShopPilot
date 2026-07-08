"""Pricing analysis module."""

from statistics import median
from typing import Any, Dict, List, Optional

from app.schemas import PricingSummary, ProductListingSchema

PRICE_BUCKETS = [
    ("$0–$10", 0, 10),
    ("$10–$20", 10, 20),
    ("$20–$30", 20, 30),
    ("$30–$40", 30, 40),
    ("$40+", 40, float("inf")),
]


def _price_stats(prices: List[float]) -> Dict[str, float]:
    if not prices:
        return {"min": 0.0, "max": 0.0, "average": 0.0, "median": 0.0}
    return {
        "min": round(min(prices), 2),
        "max": round(max(prices), 2),
        "average": round(sum(prices) / len(prices), 2),
        "median": round(median(prices), 2),
    }


def _bucket_counts(listings: List[ProductListingSchema]) -> List[Dict[str, Any]]:
    counts = {label: 0 for label, _, _ in PRICE_BUCKETS}
    for listing in listings:
        if not listing.price or listing.price <= 0:
            continue
        for label, low, high in PRICE_BUCKETS:
            if low <= listing.price < high:
                counts[label] += 1
                break
    return [{"range": label, "count": counts[label]} for label, _, _ in PRICE_BUCKETS]


def _pricing_recommendation(user_avg: float, competitor_avg: float, suggested_min: float, suggested_max: float) -> str:
    if user_avg <= 0 and competitor_avg <= 0:
        return "Collect more priced listings to generate a pricing recommendation."
    if competitor_avg <= 0:
        return f"Target the suggested range of ${suggested_min:.2f}–${suggested_max:.2f} based on your catalog median."
    delta = user_avg - competitor_avg
    if delta < -5:
        return (
            f"Your average price (${user_avg:.2f}) is below competitors (${competitor_avg:.2f}). "
            f"Consider raising prices toward ${suggested_min:.2f}–${suggested_max:.2f} while improving titles and imagery."
        )
    if delta > 5:
        return (
            f"Your average price (${user_avg:.2f}) is above competitors (${competitor_avg:.2f}). "
            f"Highlight premium materials or bundle value; test prices near ${suggested_max:.2f}."
        )
    return (
        f"Your pricing aligns with competitors. Stay within ${suggested_min:.2f}–${suggested_max:.2f} "
        "and differentiate with niche keywords and product bundles."
    )


def calculate_pricing_summary(
    listings: List[ProductListingSchema],
    competitor_listings: Optional[List[ProductListingSchema]] = None,
) -> PricingSummary:
    user_prices = [listing.price for listing in listings if listing.price and listing.price > 0]
    competitor_prices = [
        listing.price for listing in (competitor_listings or []) if listing.price and listing.price > 0
    ]

    if not user_prices and not competitor_prices:
        return PricingSummary()

    user_stats = _price_stats(user_prices)
    competitor_stats = _price_stats(competitor_prices)
    reference_median = user_stats["median"] or competitor_stats["median"]
    suggested_min = round(reference_median * 0.85, 2) if reference_median else 0.0
    suggested_max = round(reference_median * 1.15, 2) if reference_median else 0.0

    underpriced = _find_outliers(listings, reference_median * 0.7, below=True) if reference_median else []
    overpriced = _find_outliers(listings, reference_median * 1.4, below=False) if reference_median else []

    all_listings = listings + (competitor_listings or [])
    return PricingSummary(
        min_price=user_stats["min"] or competitor_stats["min"],
        max_price=user_stats["max"] or competitor_stats["max"],
        average_price=user_stats["average"] or competitor_stats["average"],
        median_price=user_stats["median"] or competitor_stats["median"],
        suggested_min=suggested_min,
        suggested_max=suggested_max,
        underpriced=underpriced,
        overpriced=overpriced,
        competitor_min_price=competitor_stats["min"],
        competitor_max_price=competitor_stats["max"],
        competitor_average_price=competitor_stats["average"],
        competitor_median_price=competitor_stats["median"],
        user_average_price=user_stats["average"],
        price_buckets=_bucket_counts(all_listings),
        pricing_recommendation=_pricing_recommendation(
            user_stats["average"], competitor_stats["average"], suggested_min, suggested_max
        ),
    )


def _find_outliers(listings: List[ProductListingSchema], threshold: float, below: bool) -> List[Dict[str, Any]]:
    results = []
    for listing in listings:
        if not listing.price:
            continue
        if below and listing.price < threshold:
            results.append({"title": listing.title, "price": listing.price, "shop_name": listing.shop_name})
        elif not below and listing.price > threshold:
            results.append({"title": listing.title, "price": listing.price, "shop_name": listing.shop_name})
    return results[:5]
