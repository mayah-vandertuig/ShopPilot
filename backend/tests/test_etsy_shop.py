"""Tests for Etsy shop name input."""

from app.adapters.etsy import EtsyAdapter


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
  assert adapter.build_shop_url("ArtStudioCo") == "https://www.etsy.com/shop/ArtStudioCo"
