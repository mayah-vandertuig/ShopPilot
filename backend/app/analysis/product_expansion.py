"""Product expansion suggestions."""

from typing import Dict, List

from app.schemas import ProductListingSchema


def suggest_expansion(listings: List[ProductListingSchema], trends: List[dict], competitors: List[dict]) -> List[Dict]:
  ideas = [
    {
      "category": "product_expansion",
      "recommendation": "Minimalist Line Art Triptych Set",
      "reasoning": "Competitors show strong demand for line art; bundle sets increase AOV.",
      "confidence": 0.82,
    },
    {
      "category": "product_expansion",
      "recommendation": "Neutral Beige Abstract Canvas Collection",
      "reasoning": "Beige and neutral tones recur across top listings and trend analysis.",
      "confidence": 0.78,
    },
    {
      "category": "product_expansion",
      "recommendation": "Scandinavian Botanical Print Series",
      "reasoning": "Botanical and Scandinavian styles are underrepresented relative to search demand.",
      "confidence": 0.75,
    },
    {
      "category": "product_expansion",
      "recommendation": "Office-Ready Small Format Prints (8x10)",
      "reasoning": "Office use-case appears in listings; smaller formats suit lower price entry points.",
      "confidence": 0.71,
    },
  ]
  return ideas
