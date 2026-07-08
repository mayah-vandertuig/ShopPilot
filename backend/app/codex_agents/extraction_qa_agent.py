"""Extraction QA Codex agent."""

import json
from typing import Any, Dict, List

from app.codex_agents.codex_client import CodexClient


class ExtractionQAAgent:
  REQUIRED_FIELDS = ["title", "price", "url", "shop_name"]

  def __init__(self):
    self.client = CodexClient()

  def evaluate(self, platform: str, raw_content: str, parsed_listings: List[dict]) -> Dict[str, Any]:
    if not self.client.is_enabled:
      return {
        "success": False,
        "enabled": False,
        "message": "Codex agents are disabled.",
        "extraction_score": 0,
        "missing_fields": [],
        "recommendations": [],
      }

    missing = self._find_missing_fields(parsed_listings)
    score = self._calculate_score(parsed_listings, missing)

    result = self.client.extraction_qa(platform, raw_content, parsed_listings)
    return {
      "success": True,
      "enabled": True,
      "message": result.get("message", ""),
      "extraction_score": score,
      "missing_fields": missing,
      "suspicious_values": self._find_suspicious(parsed_listings),
      "recommendations": [
        "Verify CSS selectors match current page structure",
        "Add fallback parsing for missing price fields",
        "Include fixture HTML tests for regression detection",
      ],
    }

  def _find_missing_fields(self, listings: List[dict]) -> List[str]:
    missing = set()
    for listing in listings:
      for field in self.REQUIRED_FIELDS:
        if not listing.get(field):
          missing.add(field)
    return sorted(missing)

  def _calculate_score(self, listings: List[dict], missing: List[str]) -> float:
    if not listings:
      return 0.0
    field_score = 1.0 - (len(missing) / (len(self.REQUIRED_FIELDS) or 1))
    fill_rate = sum(1 for l in listings if l.get("title") and l.get("price")) / len(listings)
    return round((field_score * 0.5 + fill_rate * 0.5) * 100, 1)

  def _find_suspicious(self, listings: List[dict]) -> List[str]:
    suspicious = []
    for l in listings:
      if l.get("price", 0) == 0:
        suspicious.append(f"Zero price: {l.get('title', 'unknown')[:40]}")
      if l.get("title", "") == "Untitled":
        suspicious.append("Untitled listing detected")
    return suspicious[:5]
