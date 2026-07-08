from app.analysis.listing_audit import audit_listings
from app.analysis.pricing import calculate_pricing_summary
from app.schemas import ProductListingSchema


def test_detects_short_title():
  listings = [ProductListingSchema(platform="etsy", title="Art", price=30.0)]
  pricing = calculate_pricing_summary(listings)
  issues = audit_listings(listings, 1, pricing, ["minimalist"])
  assert any(i["category"] == "title" for i in issues)
