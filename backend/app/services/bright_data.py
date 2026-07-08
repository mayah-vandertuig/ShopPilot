"""Bright Data integration service."""

import json
import logging
from contextlib import contextmanager
from typing import Any, Iterator, List, Optional, Tuple
from urllib.parse import urlparse

from app.config import get_settings

logger = logging.getLogger(__name__)

# Bright Data SDK default timeout is 30s — too low for Etsy.
CLIENT_TIMEOUT = 180
SCRAPE_POLL_TIMEOUT = 180
UNLOCKER_TIMEOUT = 120
CRAWLER_POLL_TIMEOUT = 180
ETSY_PRODUCTS_DATASET_ID = "gd_ltppk0jdv1jqz25mz"


def _sdk_import_error() -> Optional[str]:
  try:
    from brightdata import SyncBrightDataClient  # noqa: F401
    return None
  except ImportError:
    return "brightdata-sdk is not installed (pip install brightdata-sdk)"


@contextmanager
def _sync_client(token: str) -> Iterator[Any]:
  from brightdata import SyncBrightDataClient

  with SyncBrightDataClient(token=token, timeout=CLIENT_TIMEOUT) as client:
    yield client


def _is_etsy_url(url: str) -> bool:
  host = urlparse(url).netloc.lower()
  return host.endswith("etsy.com")


def _content_from_scrape_result(result: Any) -> Tuple[str, Optional[str]]:
  if result is None:
    return "", "No scrape result returned"

  if hasattr(result, "success") and not result.success:
    return "", getattr(result, "error", None) or f"Scrape failed with status {getattr(result, 'status', 'error')}"

  data = getattr(result, "data", result)
  if data is None:
    return "", "Bright Data returned no data"

  if isinstance(data, str):
    return (data, None) if data.strip() else ("", "Bright Data returned empty HTML")

  if isinstance(data, (dict, list)):
    if not data:
      return "", "Bright Data returned empty structured data"
    return json.dumps(data), None

  text = str(data)
  return (text, None) if text.strip() else ("", "Bright Data returned empty content")


def _content_from_crawl_result(result: Any) -> Tuple[str, Optional[str]]:
  if not getattr(result, "success", False):
    return "", getattr(result, "error", None) or "Crawler request failed"

  records = getattr(result, "data", None) or []
  if not records:
    return "", "Crawler returned no records"

  record = records[0]
  if isinstance(record, dict) and record.get("error"):
    return "", str(record["error"])

  if isinstance(record, dict):
    for key in ("page_html", "html", "html2text", "markdown", "content"):
      value = record.get(key)
      if isinstance(value, str) and value.strip():
        return value, None

  return "", "Crawler record had no HTML content"


def _dataset_scrape_by_url(client: Any, dataset_id: str, url: str) -> Any:
  from brightdata.scrapers.api_client import DatasetAPIClient
  from brightdata.scrapers.workflow import WorkflowExecutor

  async def _run():
    engine = client._async_client.engine
    api = DatasetAPIClient(engine)
    workflow = WorkflowExecutor(api, platform_name="etsy")
    return await workflow.execute(
      payload=[{"url": url}],
      dataset_id=dataset_id,
      poll_timeout=SCRAPE_POLL_TIMEOUT,
    )

  return client._run(_run())


class BrightDataService:
  def __init__(self):
    self.settings = get_settings()

  @property
  def is_available(self) -> bool:
    return bool(self.settings.has_bright_data and not _sdk_import_error())

  def unavailable_reason(self) -> str:
    if not self.settings.has_bright_data:
      return "No Bright Data API key found. Set BRIGHT_DATA_API_KEY or BRIGHTDATA_API_TOKEN in .env"
    sdk_error = _sdk_import_error()
    if sdk_error:
      return sdk_error
    return "Bright Data is not available"

  def _attempts_for_url(self, url: str, platform: str) -> List[str]:
    is_etsy = platform == "etsy" or _is_etsy_url(url)
    if is_etsy and "/listing/" in url:
      return ["etsy_dataset", "unlocker_async", "unlocker_sync", "crawler_async"]
    if is_etsy:
      # Search/shop pages: unlocker is faster and avoids the crawler's 30s inline timeout.
      return ["unlocker_async", "unlocker_sync", "crawler_async"]
    return ["unlocker_sync", "unlocker_async", "crawler_async"]

  def _try_etsy_dataset(self, client: Any, url: str) -> Tuple[str, Optional[str]]:
    result = _dataset_scrape_by_url(client, ETSY_PRODUCTS_DATASET_ID, url)
    return _content_from_scrape_result(result)

  def _try_crawler_async(self, client: Any, url: str) -> Tuple[str, Optional[str]]:
    job = client.crawler.trigger(url)
    result = client.crawler.download(job.snapshot_id, poll_timeout=CRAWLER_POLL_TIMEOUT)
    return _content_from_crawl_result(result)

  def _try_unlocker(self, client: Any, url: str, country: str, mode: str) -> Tuple[str, Optional[str]]:
    kwargs = {
      "country": country,
      "response_format": "raw",
      "mode": mode,
    }
    if mode == "sync":
      kwargs["timeout"] = UNLOCKER_TIMEOUT
    else:
      kwargs["poll_timeout"] = SCRAPE_POLL_TIMEOUT

    result = client.scrape_url(url, **kwargs)
    return _content_from_scrape_result(result)

  def scrape_url(
    self,
    url: str,
    country: str = "",
    platform: str = "",
  ) -> Tuple[str, str, Optional[str]]:
    """Scrape URL. Returns (content, data_source, error_message)."""
    if not self.settings.has_bright_data:
      return "", "failed", self.unavailable_reason()

    sdk_error = _sdk_import_error()
    if sdk_error:
      logger.warning(sdk_error)
      return "", "failed", sdk_error

    attempts = self._attempts_for_url(url, platform)
    errors: List[str] = []

    try:
      with _sync_client(self.settings.bright_data_token) as client:
        for attempt in attempts:
          try:
            if attempt == "etsy_dataset":
              content, error = self._try_etsy_dataset(client, url)
            elif attempt == "crawler_async":
              content, error = self._try_crawler_async(client, url)
            elif attempt == "unlocker_async":
              content, error = self._try_unlocker(client, url, country, mode="async")
            else:
              content, error = self._try_unlocker(client, url, country, mode="sync")

            if content:
              logger.info("Bright Data scrape succeeded via %s for %s", attempt, url)
              return content, "live", None

            message = error or "empty response"
            errors.append(f"{attempt}: {message}")
            logger.warning("Bright Data %s returned no content for %s (%s)", attempt, url, message)
          except Exception as e:
            message = str(e)
            errors.append(f"{attempt}: {message}")
            logger.warning("Bright Data %s failed for %s: %s", attempt, url, message)
    except Exception as e:
      msg = f"Bright Data scrape failed: {e}"
      logger.warning("%s for %s", msg, url)
      return "", "failed", msg

    summary = "; ".join(errors) if errors else "All Bright Data scrape strategies returned empty content"
    return "", "failed", summary

  def search_marketplace(self, platform: str, query: str, country: str) -> Tuple[List[dict], str, Optional[str]]:
    from app.adapters import get_adapter

    adapter = get_adapter(platform)
    url = adapter.build_search_url(query, country)
    content, source, error = self.scrape_url(url, country=country, platform=platform)
    if not content:
      return [], "failed", error
    listings = adapter.parse_listings(content)
    if not listings:
      block_reason = getattr(adapter, "detect_block_page", lambda _content: None)(content)
      if block_reason:
        return [], "failed", block_reason
      return [], "failed", (
        "Live page was scraped but the adapter could not parse listings. "
        "The marketplace HTML may have changed or blocked the request."
      )
    return [l.model_dump() for l in listings], source, None

  def scrape_shop(self, platform: str, shop_url: str, country: str = "") -> Tuple[List[dict], str, Optional[str]]:
    from app.adapters import get_adapter

    content, source, error = self.scrape_url(shop_url, country=country, platform=platform)
    if not content:
      return [], "failed", error
    adapter = get_adapter(platform)
    listings = adapter.parse_listings(content)
    if not listings:
      return [], "failed", "Live shop page scraped but no listings could be parsed"
    return [l.model_dump() for l in listings], source, None

  def scrape_product(self, platform: str, product_url: str, country: str = "") -> Tuple[Optional[dict], str, Optional[str]]:
    from app.adapters import get_adapter

    content, source, error = self.scrape_url(product_url, country=country, platform=platform)
    if not content:
      return None, "failed", error
    adapter = get_adapter(platform)
    listings = adapter.parse_listings(content)
    if listings:
      return listings[0].model_dump(), source, None
    return None, "failed", "Live product page scraped but could not be parsed"
