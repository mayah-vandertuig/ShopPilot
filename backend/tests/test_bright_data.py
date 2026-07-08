"""Tests for Bright Data service."""

from unittest.mock import MagicMock, patch

from app.services.bright_data import (
  BrightDataService,
  _content_from_crawl_result,
  _content_from_scrape_result,
)


def test_content_from_scrape_result_handles_structured_data():
  result = MagicMock()
  result.success = True
  result.data = {"title": "Test listing", "url": "https://www.etsy.com/listing/1"}
  content, error = _content_from_scrape_result(result)
  assert error is None
  assert '"title": "Test listing"' in content


def test_content_from_crawl_result_prefers_page_html():
  result = MagicMock()
  result.success = True
  result.data = [{"page_html": "<html>etsy</html>"}]
  content, error = _content_from_crawl_result(result)
  assert error is None
  assert content == "<html>etsy</html>"


def test_scrape_url_falls_back_to_crawler(monkeypatch):
  monkeypatch.setenv("BRIGHTDATA_API_TOKEN", "test-token")

  from app.config import get_settings
  get_settings.cache_clear()

  empty_result = MagicMock()
  empty_result.success = True
  empty_result.data = ""

  crawl_result = MagicMock()
  crawl_result.success = True
  crawl_result.data = [{"page_html": "<html>etsy listing</html>"}]

  mock_client = MagicMock()
  mock_client.scrape_url.return_value = empty_result
  mock_client.crawler.crawl.return_value = crawl_result

  mock_cm = MagicMock()
  mock_cm.__enter__.return_value = mock_client
  mock_cm.__exit__.return_value = False

  with patch("brightdata.SyncBrightDataClient", return_value=mock_cm):
    service = BrightDataService()
    content, source, error = service.scrape_url(
      "https://www.etsy.com/search?q=frames",
      country="US",
      platform="etsy",
    )

  assert error is None
  assert source == "live"
  assert "etsy listing" in content
  mock_client.crawler.crawl.assert_called_once()

  get_settings.cache_clear()
