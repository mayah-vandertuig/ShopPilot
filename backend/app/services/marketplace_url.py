"""Marketplace URL localization helpers."""

from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


def _language_code(language: str) -> str:
    return (language or "en-US").split("-")[0].lower()


def _country_code(country: str) -> str:
    code = (country or "US").upper()
    return "uk" if code == "UK" else code.lower()


def _set_query_param(query: dict, key: str, value: str, overwrite: bool = False) -> None:
    if overwrite or key not in query or not query[key][0]:
        query[key] = [value]


def _normalize_google_url(url: str, country: str, language: str, currency: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    _set_query_param(query, "hl", _language_code(language), overwrite=True)
    _set_query_param(query, "gl", _country_code(country), overwrite=True)
    if currency:
        _set_query_param(query, "currency", currency.upper(), overwrite=True)
    flat = {key: values[0] for key, values in query.items() if values}
    return urlunparse(parsed._replace(query=urlencode(flat)))


def _normalize_etsy_url(url: str, country: str, language: str, currency: str) -> str:
    from app.adapters.etsy import with_etsy_locale

    return with_etsy_locale(url, country=country, currency=currency, language=language)


def normalize_marketplace_url(
    url: str,
    platform: str,
    country: str = "US",
    language: str = "en-US",
    currency: str = "USD",
    locale: str = "en_US",
) -> str:
    """Add platform-specific locale params where supported."""
    if not url:
        return url

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    platform_key = (platform or "").lower()

    if platform_key == "google_shopping" or "google." in host:
        return _normalize_google_url(url, country, language, currency)

    if platform_key == "etsy" or host.endswith("etsy.com"):
        return _normalize_etsy_url(url, country, language, currency)

    query = parse_qs(parsed.query, keep_blank_values=True)
    changed = False
    for key, value in (
        ("hl", _language_code(language)),
        ("gl", _country_code(country)),
        ("lang", _language_code(language)),
        ("locale", locale.replace("_", "-") if locale else ""),
        ("currency", currency.upper() if currency else ""),
    ):
        if key in query:
            _set_query_param(query, key, value, overwrite=True)
            changed = True

    if not changed:
        return url

    flat = {key: values[0] for key, values in query.items() if values}
    return urlunparse(parsed._replace(query=urlencode(flat)))
