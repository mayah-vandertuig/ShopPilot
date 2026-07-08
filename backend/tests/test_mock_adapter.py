from app.adapters.mock import MockAdapter


def test_mock_loads_seed_data():
  adapter = MockAdapter()
  listings = adapter.get_listings_for_platform("etsy")
  assert len(listings) >= 25


def test_mock_keyword_filter():
  adapter = MockAdapter()
  listings = adapter.get_listings_for_platform("etsy", "minimalist")
  assert len(listings) > 0
