"""Listing advisor agent."""

from typing import Any, Dict, List

from app.services.ai import AIService


class ListingAdvisorAgent:
  def __init__(self):
    self.ai = AIService()

  def advise(self, listing: dict, competitors: List[dict], pricing_summary: dict, keyword_summary: dict) -> Dict[str, Any]:
    context = {
      "listing": listing,
      "competitors": competitors[:5],
      "pricing_summary": pricing_summary,
      "keyword_summary": keyword_summary,
    }
    recs = self.ai.generate_listing_recommendations(context)
    return {
      "improved_title": next((r["recommendation"] for r in recs if r.get("category") == "title"), ""),
      "improved_description": next((r["recommendation"] for r in recs if r.get("category") == "description"), ""),
      "suggested_tags": next((r["recommendation"] for r in recs if r.get("category") == "tags"), ""),
      "pricing_recommendation": next((r["recommendation"] for r in recs if r.get("category") == "pricing"), ""),
      "positioning_recommendation": next((r["recommendation"] for r in recs if r.get("category") == "positioning"), ""),
      "explanation": "; ".join(r.get("reasoning", "") for r in recs[:2]),
      "confidence": sum(r.get("confidence", 0) for r in recs) / max(len(recs), 1),
      "recommendations": recs,
    }
