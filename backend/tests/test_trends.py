"""Tests for trend detection."""

from app.analysis.trends import detect_trends
from app.schemas import ProductListingSchema


def _listing(title: str, tags: list[str] | None = None) -> ProductListingSchema:
  return ProductListingSchema(
    platform="etsy",
    title=title,
    url="https://www.etsy.com/listing/1/sample",
    tags=tags or [],
  )


def test_detect_trends_from_repeated_title_words():
  listings = [
    _listing("Minimalist canvas wall art print"),
    _listing("Minimalist bedroom wall art poster"),
    _listing("Abstract canvas wall decor"),
  ]
  trends = detect_trends(listings, analysis_id=1)
  assert trends
  assert any(trend["trend_name"].lower() == "minimalist" for trend in trends)


def test_detect_trends_with_small_catalog():
  listings = [_listing("Handmade ceramic mug gift")]
  trends = detect_trends(listings, analysis_id=1)
  assert trends
