# Bright Data Integration

ShopPilot uses the Bright Data SDK for marketplace data collection.

## Configuration

Set `BRIGHT_DATA_API_KEY` in your `.env` file.

## Service

The `BrightDataService` in `backend/app/services/bright_data.py` exposes:

- `scrape_url(url)` — scrape a single URL
- `search_marketplace(platform, query, country)` — search by platform
- `scrape_shop(platform, shop_url)` — scrape a shop page
- `scrape_product(platform, product_url)` — scrape a product page

## Fallback Behavior

| Condition | Behavior |
|-----------|----------|
| Missing API key | Mock data |
| API failure | Mock data |
| Parse failure | Mock data |

All responses include a `data_source` field: `"live"` or `"mock"`.

## SDK Usage

```python
from brightdata import SyncBrightDataClient

client = SyncBrightDataClient(token="...")
result = client.scrape_url(url)
html_or_text = result.data
```
