from app.analysis.pricing import calculate_pricing_summary
from app.schemas import ProductListingSchema


def test_empty_listings():
  summary = calculate_pricing_summary([])
  assert summary.min_price == 0.0


def test_single_listing():
  listings = [ProductListingSchema(platform="etsy", title="Test", price=50.0)]
  summary = calculate_pricing_summary(listings)
  assert summary.average_price == 50.0
  assert summary.median_price == 50.0
