"""Listing audit module."""

from typing import Any, Dict, List

from app.schemas import PricingSummary, ProductListingSchema


def audit_listings(
  listings: List[ProductListingSchema],
  analysis_id: int,
  pricing: PricingSummary,
  top_keywords: List[str],
) -> List[Dict[str, Any]]:
  issues = []
  generic_titles = {"wall art", "print", "poster", "canvas", "home decor"}

  for i, listing in enumerate(listings):
    listing_id = i + 1

    if len(listing.title) < 25:
      issues.append(_issue(analysis_id, listing_id, "high", "title",
        f"Title too short ({len(listing.title)} chars): '{listing.title}'",
        "Expand title with style, material, size, and use-case keywords."))

    if listing.title.lower().strip() in generic_titles:
      issues.append(_issue(analysis_id, listing_id, "high", "title",
        f"Title is too generic: '{listing.title}'",
        "Add specific descriptors: minimalist, abstract, Scandinavian, line art, etc."))

    if len(listing.description) < 50:
      issues.append(_issue(analysis_id, None, "medium", "description",
        f"Thin description for '{listing.title[:40]}...'",
        "Add material, sizing, framing options, and room placement details."))

    if not listing.tags:
      issues.append(_issue(analysis_id, listing_id, "medium", "tags",
        f"No tags detected for '{listing.title[:40]}'",
        "Add 10-13 relevant tags covering style, color, and occasion."))

    if listing.price and pricing.median_price:
      if listing.price < pricing.median_price * 0.6:
        issues.append(_issue(analysis_id, listing_id, "medium", "pricing",
          f"Potentially underpriced at ${listing.price}",
          f"Consider pricing closer to ${pricing.suggested_min}-${pricing.suggested_max} range."))
      elif listing.price > pricing.median_price * 1.5:
        issues.append(_issue(analysis_id, listing_id, "low", "pricing",
          f"Premium priced at ${listing.price}",
          "Ensure premium pricing is justified with quality signals in title and reviews."))

    title_words = set(listing.title.lower().split())
    missing_kw = [kw for kw in top_keywords[:5] if kw not in title_words]
    if missing_kw and len(missing_kw) >= 3:
      issues.append(_issue(analysis_id, listing_id, "low", "keywords",
        f"Missing popular keywords: {', '.join(missing_kw[:3])}",
        "Incorporate trending niche keywords into title and tags."))

  return issues


def _issue(analysis_id, listing_id, severity, category, issue, suggestion) -> Dict[str, Any]:
  return {
    "analysis_id": analysis_id,
    "listing_id": listing_id,
    "severity": severity,
    "category": category,
    "issue": issue,
    "suggestion": suggestion,
  }
