"""Listing normalization utilities."""

from typing import List

from app.schemas import ProductListingSchema


def normalize_listings(listings: List[ProductListingSchema], currency: str = "USD") -> List[ProductListingSchema]:
  for listing in listings:
    if not listing.currency:
      listing.currency = currency
    listing.title = listing.title.strip()
    listing.shop_name = listing.shop_name.strip() or "Unknown Shop"
    listing.tags = [t.strip().lower() for t in listing.tags if t.strip()]
    if not listing.detected_keywords:
      listing.detected_keywords = [w.lower() for w in listing.title.split() if len(w) > 3]
  return listings
