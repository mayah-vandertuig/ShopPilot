"""Tests for Etsy adapter parsing."""

import json

from app.adapters.etsy import EtsyAdapter


def test_parse_listings_from_json_ld_search_listitem():
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
  assert listings[0].url == "https://www.etsy.com/listing/1"


def test_parse_listings_from_json_ld_direct_product_items():
  adapter = EtsyAdapter()
  payload = {
    "@type": "ItemList",
    "itemListElement": [
      {
        "@type": "Product",
        "name": "Wood laptop stand",
        "url": "https://www.etsy.com/listing/1575517454/wood-laptop-stand",
        "brand": {"@type": "Brand", "name": "YiYoYo"},
        "offers": {"price": "39.20", "priceCurrency": "USD"},
        "aggregateRating": {"ratingValue": "4.8", "reviewCount": "501"},
      }
    ],
  }
  listings = adapter.parse_listings(json.dumps(payload))
  assert len(listings) == 1
  assert listings[0].shop_name == "YiYoYo"
  assert listings[0].price == 39.2
  assert listings[0].review_count == 501


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


def test_parse_listings_from_modern_html_cards():
  adapter = EtsyAdapter()
  html = """
  <html><body>
    <div data-listing-id="12345" class="wt-height-full">
      <a href="https://www.etsy.com/listing/12345/minimal-wall-art">
        <h3 class="wt-text-caption">Minimal Wall Art Print</h3>
      </a>
      <p class="lc-price wt-text-title-01"><span class="currency-symbol">$</span>18.00</p>
      <p class="v2-listing-card__shop">ArtStudioCo</p>
      <img src="https://i.etsystatic.com/example.jpg" />
    </div>
  </body></html>
  """
  listings = adapter.parse_listings(html)
  assert len(listings) == 1
  assert listings[0].title == "Minimal Wall Art Print"
  assert listings[0].price == 18.0
  assert listings[0].shop_name == "ArtStudioCo"


def test_parse_listings_from_markdown_links():
  adapter = EtsyAdapter()
  markdown = """
  # Results
  [Minimal frame mockup](https://www.etsy.com/listing/1751739997/simple-vertical-frame-mockup)
  """
  listings = adapter.parse_listings(markdown)
  assert len(listings) == 1
  assert listings[0].url == "https://www.etsy.com/listing/1751739997"
  assert "frame" in listings[0].title.lower()


def test_parse_listings_filters_junk_titles():
  adapter = EtsyAdapter()
  html = """
  <html><body>
    <a href="https://www.etsy.com/listing/12345/real-product-title-here">
      <h3 class="wt-text-caption">Minimalist Wall Art Print on Canvas</h3>
    </a>
    <a href="https://www.etsy.com/listing/99999/favorite">
      <h3>Add to favorites</h3>
    </a>
  </body></html>
  """
  listings = adapter.parse_listings(html)
  assert len(listings) == 1
  assert "Wall Art" in listings[0].title


def test_enrich_shop_listings_sets_shop_name():
  adapter = EtsyAdapter()
  listings = [
    adapter._listing_from_record({
      "title": "Sample listing title here",
      "url": "https://www.etsy.com/listing/1/sample",
      "price": 10,
    })
  ]
  enriched = adapter.enrich_shop_listings(listings, "ArtStudioCo")
  assert enriched[0].shop_name == "ArtStudioCo"


def test_enrich_listing_tags_from_embedded_json():
  adapter = EtsyAdapter()
  payload = {
    "listings": [
      {
        "listing_id": 12345,
        "title": "Minimal Wall Art Print on Canvas",
        "url": "https://www.etsy.com/listing/12345/minimal-wall-art",
        "tags": ["wall art", "minimalist", "canvas print"],
      }
    ]
  }
  html = f'<html><script type="application/json">{json.dumps(payload)}</script></html>'
  listings = adapter.parse_listings(html)
  enriched = adapter.enrich_listing_tags(listings, html)
  assert enriched[0].tags
  assert "minimalist" in enriched[0].tags


def test_infer_tags_from_listing_title():
  adapter = EtsyAdapter()
  listing = adapter._listing_from_record({
    "title": "Minimalist Scandinavian Wall Art Print",
    "url": "https://www.etsy.com/listing/1/sample",
    "price": 10,
  })
  finalized = adapter.finalize_listings([listing])[0]
  assert finalized.tags == []
  assert finalized.detected_keywords


def test_tags_from_record_ignores_materials():
  adapter = EtsyAdapter()
  tags = adapter._tags_from_record({
    "tags": ["wall art", "minimalist print"],
    "materials": ["canvas", "wood"],
  })
  assert "wall art" in tags
  assert "canvas" not in tags


def test_parse_listings_from_nested_embedded_json():
  adapter = EtsyAdapter()
  payload = {
    "search": {
      "listings": [
        {
          "listing_id": 999,
          "title": "Nested JSON listing",
          "url": "https://www.etsy.com/listing/999/nested-json-listing",
          "price": 12.5,
          "shop_name": "NestedShop",
        }
      ]
    }
  }
  html = f'<html><script type="application/json">{json.dumps(payload)}</script></html>'
  listings = adapter.parse_listings(html)
  assert len(listings) == 1
  assert listings[0].title == "Nested JSON listing"
  assert listings[0].shop_name == "NestedShop"
