# Adding a New Marketplace Platform

## 1. Create an Adapter

Create `backend/app/adapters/your_platform.py`:

```python
from app.adapters.base import BaseMarketplaceAdapter
from app.schemas import ProductListingSchema

class YourPlatformAdapter(BaseMarketplaceAdapter):
    platform_name = "your_platform"
    supports_shop_url = True
    supports_product_url = True
    supports_keyword_search = True

    def build_search_url(self, query: str, country: str) -> str:
        return f"https://example.com/search?q={query}"

    def parse_listings(self, raw_content: str) -> list[ProductListingSchema]:
        # Parse HTML/JSON into listings
        ...

    def normalize_listing(self, raw: dict) -> ProductListingSchema:
        ...
```

## 2. Register the Adapter

Add to `backend/app/adapters/__init__.py`:

```python
ADAPTERS = {
    ...
    "your_platform": YourPlatformAdapter,
}
```

## 3. Add Tests

Create `backend/tests/test_your_platform_adapter.py` with parsing tests using fixture HTML.

## 4. Update Frontend

Add the platform to the platform selector in `frontend/app/page.tsx`.

## 5. Document

Update the supported platforms table in `README.md`.
