"""Backend test suite."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from app.schemas import ProductListingSchema
from app.analysis.pricing import calculate_pricing_summary
from app.analysis.keywords import extract_keywords
from app.analysis.competitors import analyze_competitors
from app.analysis.listing_audit import audit_listings
from app.adapters.mock import MockAdapter


@pytest.fixture
def client():
  Base.metadata.create_all(bind=engine)
  return TestClient(app)


@pytest.fixture
def sample_listings():
  return [
    ProductListingSchema(platform="etsy", title="Minimalist Line Art Canvas", shop_name="Shop A", price=35.0, tags=["minimalist", "canvas"]),
    ProductListingSchema(platform="etsy", title="Abstract Beige Wall Print", shop_name="Shop A", price=42.0, tags=["abstract", "beige"]),
    ProductListingSchema(platform="etsy", title="Scandinavian Botanical Art", shop_name="Shop B", price=28.0, tags=["botanical"]),
    ProductListingSchema(platform="etsy", title="Geometric Neutral Poster", shop_name="Shop B", price=55.0, tags=["geometric"]),
    ProductListingSchema(platform="etsy", title="Black White Line Drawing", shop_name="Shop C", price=22.0, tags=["line art"]),
  ]


def test_health(client):
  response = client.get("/health")
  assert response.status_code == 200
  assert response.json()["status"] == "ok"


def test_pricing_calculations(sample_listings):
  summary = calculate_pricing_summary(sample_listings)
  assert summary.min_price == 22.0
  assert summary.max_price == 55.0
  assert summary.average_price == 36.4
  assert summary.median_price == 35.0
  assert summary.suggested_min > 0
  assert summary.suggested_max > summary.suggested_min


def test_keyword_extraction(sample_listings):
  summary = extract_keywords(sample_listings)
  assert len(summary.top_keywords) > 0
  assert summary.top_keywords[0]["count"] >= 1
  assert isinstance(summary.missing_opportunities, list)


def test_listing_audit(sample_listings):
  pricing = calculate_pricing_summary(sample_listings)
  keywords = extract_keywords(sample_listings)
  top_kw = [k["keyword"] for k in keywords.top_keywords]
  issues = audit_listings(sample_listings, 1, pricing, top_kw)
  assert isinstance(issues, list)


def test_mock_adapter():
  adapter = MockAdapter()
  listings = adapter.parse_listings("")
  assert len(listings) >= 25
  assert listings[0].title
  assert listings[0].price > 0


def test_competitor_grouping(sample_listings):
  competitors = analyze_competitors(sample_listings, 1, "etsy")
  assert len(competitors) == 3
  assert competitors[0]["product_count"] >= 1
  shop_a = next(c for c in competitors if c["competitor_name"] == "Shop A")
  assert shop_a["product_count"] == 2


def test_codex_disabled(client):
  response = client.get("/api/codex/status")
  assert response.status_code == 200
  data = response.json()
  assert data["enabled"] is False


def test_codex_repair_disabled(client):
  response = client.post("/api/codex/repair-adapter", json={
    "platform": "etsy",
    "failing_url": "https://etsy.com/search?q=test",
    "error_message": "parse failed",
    "adapter_file_path": "backend/app/adapters/etsy.py",
  })
  assert response.status_code == 200
  assert response.json()["enabled"] is False


def test_create_analysis(client):
  response = client.post("/api/analyses", json={
    "platform": "etsy",
    "input_type": "keyword",
    "input_value": "minimalist wall art",
    "country": "US",
    "currency": "USD",
  })
  assert response.status_code == 200
  data = response.json()
  assert data["id"] > 0
  assert len(data["listings"]) >= 25
  assert data["pricing_summary"]["average_price"] > 0
