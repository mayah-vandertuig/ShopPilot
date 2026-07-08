"""Product expansion suggestions."""

from typing import Dict, List

from app.schemas import ProductListingSchema


def suggest_expansion(listings: List[ProductListingSchema], trends: List[dict], competitors: List[dict]) -> List[Dict]:
  """Return product expansion ideas derived from live analysis data.

  Static placeholder ideas are intentionally omitted. Use the recommendations
  API with OpenAI configured to generate expansion suggestions.
  """
  return []
