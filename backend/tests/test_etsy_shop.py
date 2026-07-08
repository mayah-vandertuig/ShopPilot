"""Tests for Etsy shop name input."""

from app.adapters.etsy import EtsyAdapter, with_etsy_locale


def test_normalize_shop_name_from_slug():
  adapter = EtsyAdapter()
  assert adapter.normalize_shop_name("CaitlynMinimalist") == "CaitlynMinimalist"


def test_normalize_shop_name_from_url():
  adapter = EtsyAdapter()
  assert adapter.normalize_shop_name("https://www.etsy.com/shop/ArtStudioCo") == "ArtStudioCo"


def test_normalize_shop_name_from_at_handle():
  adapter = EtsyAdapter()
  assert adapter.normalize_shop_name("@ArtStudioCo") == "ArtStudioCo"


def test_build_shop_url():
  adapter = EtsyAdapter()
  assert adapter.build_shop_url("ArtStudioCo") == (
    "https://www.etsy.com/shop/ArtStudioCo?locale_override=en-US&ship_to=US&currency=USD"
  )


def test_with_etsy_locale_adds_english_override():
  url = with_etsy_locale("https://www.etsy.com/search?q=art", country="US")
  assert "locale_override=en-US" in url
  assert "ship_to=US" in url
  assert "currency=USD" in url
