"""Tests for Etsy adapter parsing."""

import json

from app.adapters.etsy import EtsyAdapter


def test_parse_listings_from_json_ld_search():
  adapter = EtsyAdapter()
  payload = {
    "@type": "ItemList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "item": {
          "@type": "Product",
          "name": "Minimal frame",
          "url": "https://www.etsy.com/listing/1/minimal-frame",
          "offers": {"price": "24.00", "priceCurrency": "USD"},
        },
      }
    ],
  }
  html = f'<html><script type="application/ld+json">{json.dumps(payload)}</script></html>'
  listings = adapter.parse_listings(html)
  assert len(listings) == 1
  assert listings[0].title == "Minimal frame"
  assert listings[0].price == 24.0


def test_parse_listings_from_structured_dataset_json():
  adapter = EtsyAdapter()
  payload = [{
    "title": "Dataset listing",
    "url": "https://www.etsy.com/listing/2/dataset-listing",
    "price": 19.5,
    "shop_name": "MockShop",
  }]
  listings = adapter.parse_listings(json.dumps(payload))
  assert len(listings) == 1
  assert listings[0].shop_name == "MockShop"
  assert listings[0].price == 19.5
