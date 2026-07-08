from app.analysis.competitors import analyze_competitors
from app.schemas import ProductListingSchema


def test_groups_by_shop():
  listings = [
    ProductListingSchema(platform="etsy", title="A", shop_name="Shop1", price=10, review_count=5),
    ProductListingSchema(platform="etsy", title="B", shop_name="Shop1", price=20, review_count=3),
    ProductListingSchema(platform="etsy", title="C", shop_name="Shop2", price=30, review_count=10),
  ]
  result = analyze_competitors(listings, 1, "etsy")
  assert len(result) == 2
  shop1 = next(r for r in result if r["competitor_name"] == "Shop1")
  assert shop1["product_count"] == 2
  assert shop1["total_reviews"] == 8
