"""Tests for marketplace localization."""

from app.adapters.etsy import EtsyAdapter
from app.adapters.google_shopping import GoogleShoppingAdapter
from app.schemas import AnalysisCreate
from app.services.bright_data import BrightDataService
from app.services.localization import LOCALE_MISMATCH_WARNING, detect_unexpected_locale
from app.services.marketplace_url import normalize_marketplace_url


def test_google_shopping_search_url_includes_hl_en_and_gl_us():
    adapter = GoogleShoppingAdapter()
    url = adapter.build_search_url("minimalist wall art")
    assert "hl=en" in url
    assert "gl=us" in url


def test_etsy_search_url_preserves_query_and_includes_us_currency_hints():
    adapter = EtsyAdapter()
    url = adapter.build_search_url("minimalist wall art")
    assert "q=minimalist+wall+art" in url
    assert "ship_to=US" in url
    assert "currency=USD" in url
    assert "locale_override=en-US" in url


def test_normalize_marketplace_url_overrides_existing_locale_params():
    url = normalize_marketplace_url(
        "https://www.etsy.com/search?q=art&locale_override=es-ES&ship_to=ES&currency=EUR",
        platform="etsy",
        country="US",
        language="en-US",
        currency="USD",
        locale="en_US",
    )
    assert "locale_override=en-US" in url
    assert "ship_to=US" in url
    assert "currency=USD" in url


def test_normalize_marketplace_url_preserves_existing_query_params():
    url = normalize_marketplace_url(
        "https://www.etsy.com/search?q=art&sort_order=date",
        platform="etsy",
        country="US",
        language="en-US",
        currency="USD",
        locale="en_US",
    )
    assert "q=art" in url
    assert "sort_order=date" in url
    assert "ship_to=US" in url


def test_analysis_create_defaults_to_us_english():
    request = AnalysisCreate(
        platform="etsy",
        input_type="keyword",
        input_value="minimalist wall art",
    )
    assert request.country == "US"
    assert request.language == "en-US"
    assert request.locale == "en_US"
    assert request.currency == "USD"


def test_detect_unexpected_locale_warns_for_spanish_content():
    spanish_html = """
    <html><body>
      <button>Añadir al carrito</button>
      <span>Precio</span>
      <span>Envío gratis</span>
      <span>Resultados de búsqueda</span>
      <span>Artículo vendido</span>
    </body></html>
    """
    warning = detect_unexpected_locale(spanish_html, "en-US")
    assert warning == LOCALE_MISMATCH_WARNING


def test_search_marketplace_returns_locale_warning_for_spanish_content(monkeypatch):
    from unittest.mock import MagicMock, patch

    monkeypatch.setenv("BRIGHTDATA_API_TOKEN", "test-token")

    from app.config import get_settings
    get_settings.cache_clear()

    spanish_html = """
    <html><body>
      <button>Añadir al carrito</button>
      <span>Precio</span>
      <span>Envío gratis</span>
      <span>Resultados de búsqueda</span>
      <span>Artículo vendido</span>
    </body></html>
    """

    unlocker_result = MagicMock()
    unlocker_result.success = True
    unlocker_result.data = spanish_html

    mock_client = MagicMock()
    mock_client.scrape_url.return_value = unlocker_result

    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_client
    mock_cm.__exit__.return_value = False

    with patch("brightdata.SyncBrightDataClient", return_value=mock_cm):
        service = BrightDataService()
        listings, source, error, warning = service.search_marketplace(
            "google_shopping",
            "minimalist wall art",
            country="US",
            language="en-US",
        )

    assert error is None
    assert warning is not None
    assert LOCALE_MISMATCH_WARNING in warning
    assert source in {"live", "mock"}

    get_settings.cache_clear()
