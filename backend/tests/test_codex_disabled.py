from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_codex_status_endpoint():
  r = client.get("/api/codex/status")
  assert r.status_code == 200
  assert "enabled" in r.json()


def test_codex_extraction_qa_disabled():
  r = client.post("/api/codex/extraction-qa", json={"platform": "etsy", "parsed_listings": []})
  assert r.status_code == 200
  assert r.json()["enabled"] is False


def test_codex_generate_tests_disabled():
  r = client.post("/api/codex/generate-tests", json={
    "target_file": "backend/app/adapters/etsy.py",
    "behavior_description": "parses Etsy listings",
  })
  assert r.status_code == 200
  assert r.json()["enabled"] is False
