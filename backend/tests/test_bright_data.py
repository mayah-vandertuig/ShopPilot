"""Tests for Bright Data service."""

from unittest.mock import MagicMock, patch

from app.services.bright_data import (
  BrightDataService,
  CLIENT_TIMEOUT,
  FAST_SCRAPE_POLL_TIMEOUT,
  SCRAPE_POLL_TIMEOUT,
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


def test_sync_client_uses_extended_timeout():
  with patch("brightdata.SyncBrightDataClient") as mock_ctor:
    mock_cm = MagicMock()
    mock_ctor.return_value = mock_cm
    from app.services.bright_data import _sync_client

    with _sync_client("test-token"):
      pass

    mock_ctor.assert_called_once_with(token="test-token", timeout=CLIENT_TIMEOUT)


def test_etsy_search_prefers_unlocker_before_crawler(monkeypatch):
  monkeypatch.setenv("BRIGHTDATA_API_TOKEN", "test-token")

  from app.config import get_settings
  get_settings.cache_clear()

  unlocker_result = MagicMock()
  unlocker_result.success = True
  unlocker_result.data = "<html>etsy search</html>"

  mock_client = MagicMock()
  mock_client.scrape_url.return_value = unlocker_result

  mock_cm = MagicMock()
  mock_cm.__enter__.return_value = mock_client
  mock_cm.__exit__.return_value = False

  with patch("brightdata.SyncBrightDataClient", return_value=mock_cm):
    service = BrightDataService()
    content, source, error, _ = service.scrape_url(
      "https://www.etsy.com/search?q=frames",
      country="US",
      platform="etsy",
    )

  assert error is None
  assert source == "live"
  assert "etsy search" in content
  mock_client.scrape_url.assert_called()
  mock_client.crawler.trigger.assert_not_called()

  get_settings.cache_clear()


def test_fast_mode_uses_short_timeout_and_single_attempt(monkeypatch):
  monkeypatch.setenv("BRIGHTDATA_API_TOKEN", "test-token")

  from app.config import get_settings
  get_settings.cache_clear()

  empty_result = MagicMock()
  empty_result.success = False
  empty_result.error = "Polling timeout after 45s"

  mock_client = MagicMock()
  mock_client.scrape_url.return_value = empty_result

  mock_cm = MagicMock()
  mock_cm.__enter__.return_value = mock_client
  mock_cm.__exit__.return_value = False

  with patch("brightdata.SyncBrightDataClient", return_value=mock_cm):
    service = BrightDataService()
    content, source, error, _ = service.scrape_url(
      "https://www.etsy.com/shop/SanFranciscoStudio",
      country="US",
      platform="etsy",
      fast=True,
    )

  assert content == ""
  assert source == "failed"
  assert error is not None
  assert mock_client.scrape_url.call_count == 1
  assert mock_client.scrape_url.call_args.kwargs["poll_timeout"] == FAST_SCRAPE_POLL_TIMEOUT
  mock_client.crawler.trigger.assert_not_called()

  get_settings.cache_clear()


def test_normal_mode_retries_with_longer_unlocker_timeout(monkeypatch):
  monkeypatch.setenv("BRIGHTDATA_API_TOKEN", "test-token")

  from app.config import get_settings
  get_settings.cache_clear()

  empty_result = MagicMock()
  empty_result.success = False
  empty_result.error = "Polling timeout after 180s"

  mock_client = MagicMock()
  mock_client.scrape_url.return_value = empty_result
  mock_client.crawler.trigger.return_value = MagicMock(snapshot_id="snap-1")
  mock_client.crawler.download.return_value = MagicMock(success=False, error="crawler failed")

  mock_cm = MagicMock()
  mock_cm.__enter__.return_value = mock_client
  mock_cm.__exit__.return_value = False

  with patch("brightdata.SyncBrightDataClient", return_value=mock_cm):
    service = BrightDataService()
    content, source, error, _ = service.scrape_url(
      "https://www.etsy.com/shop/SanFranciscoStudio",
      country="US",
      platform="etsy",
      fast=False,
    )

  assert content == ""
  assert source == "failed"
  assert error is not None
  assert mock_client.scrape_url.call_count == 2
  assert mock_client.scrape_url.call_args_list[0].kwargs["poll_timeout"] == SCRAPE_POLL_TIMEOUT
  assert mock_client.scrape_url.call_args_list[1].kwargs["timeout"] == 120
  mock_client.crawler.trigger.assert_called_once()

  get_settings.cache_clear()
