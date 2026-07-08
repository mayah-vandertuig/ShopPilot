"""Product expansion agent."""

from typing import Any, Dict, List

from app.analysis.product_expansion import suggest_expansion
from app.schemas import ProductListingSchema


class ProductExpansionAgent:
  def expand(self, listings: List[dict], trends: List[dict], competitors: List[dict]) -> Dict[str, Any]:
    schema_listings = [
      ProductListingSchema(
        platform=l.get("platform", "etsy"),
        title=l.get("title", ""),
        price=l.get("price", 0),
        shop_name=l.get("shop_name", ""),
      )
      for l in listings
    ]
    ideas = suggest_expansion(schema_listings, trends, competitors)
    return {
      "product_ideas": [
        {
          "idea": i["recommendation"],
          "rationale": i["reasoning"],
          "suggested_price_range": "$25-$65",
          "target_keywords": ["minimalist", "wall art", "neutral"],
          "confidence": i["confidence"],
        }
        for i in ideas
      ]
    }
