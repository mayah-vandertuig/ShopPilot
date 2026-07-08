from app.schemas import ProductListingSchema
from app.services.normalization import normalize_listings


def test_normalize_preserves_empty_shop_name():
  listings = [ProductListingSchema(platform="etsy", title="Sample listing", shop_name="", price=10)]
  normalized = normalize_listings(listings)
  assert normalized[0].shop_name == ""


def test_normalize_preserves_tag_casing():
  listings = [ProductListingSchema(platform="etsy", title="Sample listing", tags=["Wall Art", "Minimalist"], price=10)]
  normalized = normalize_listings(listings)
  assert normalized[0].tags == ["Wall Art", "Minimalist"]
