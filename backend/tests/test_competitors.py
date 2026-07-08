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
  assert "match_score" in shop1


def test_ignores_listings_without_shop_name():
  listings = [
    ProductListingSchema(platform="etsy", title="A", shop_name="", price=10, review_count=5),
    ProductListingSchema(platform="etsy", title="B", shop_name="Shop2", price=30, review_count=10),
  ]
  result = analyze_competitors(listings, 1, "etsy")
  assert len(result) == 1
  assert result[0]["competitor_name"] == "Shop2"


def test_merges_shop_name_variants_by_slug():
  listings = [
    ProductListingSchema(
      platform="etsy",
      title="Minimalist Print",
      shop_name="Modern Print Lab",
      price=20,
      review_count=5,
      tags=["minimalist wall art"],
      listing_source="competitor_search",
    ),
    ProductListingSchema(
      platform="etsy",
      title="Neutral Poster",
      shop_name="ModernPrintLab",
      price=24,
      review_count=8,
      tags=["neutral wall art"],
      listing_source="competitor_search",
    ),
  ]
  result = analyze_competitors(listings, 1, "etsy")
  assert len(result) == 1
  assert result[0]["product_count"] == 2
  assert result[0]["competitor_name"] == "ModernPrintLab"
  assert "minimalist wall art" in result[0]["common_keywords"]
