# Bright Data Integration

ShopPilot uses the Bright Data SDK for marketplace data collection.

## Configuration

Set `BRIGHT_DATA_API_KEY` or `BRIGHTDATA_API_TOKEN` in your `.env` file.

Install the SDK:

```bash
pip install brightdata-sdk
```

## Service

The `BrightDataService` in `backend/app/services/bright_data.py` exposes:

- `scrape_url(url)` — scrape a single URL
- `search_marketplace(platform, query, country)` — search by platform
- `scrape_shop(platform, shop_url)` — scrape a shop page
- `scrape_product(platform, product_url)` — scrape a product page

## Failure Behavior

ShopPilot does **not** use mock marketplace data. If live collection fails, the API returns an error with a clear reason:

| Condition | Behavior |
|-----------|----------|
| Missing API key | Analysis fails with configuration error |
| SDK not installed | Analysis fails — install `brightdata-sdk` |
| API failure | Analysis fails with scrape error |
| Parse failure | Analysis fails — adapter could not parse listings |

Successful analyses are labeled `data_source: "live"`.

## SDK Usage

```python
from brightdata import SyncBrightDataClient

client = SyncBrightDataClient(token="...")
result = client.scrape_url(url)
html_or_text = result.data
```
