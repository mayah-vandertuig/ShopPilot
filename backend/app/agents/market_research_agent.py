"""Market research agent."""

from typing import Any, Dict


class MarketResearchAgent:
  def research(self, analysis_summary: Dict[str, Any]) -> Dict[str, Any]:
    pricing = analysis_summary.get("pricing_summary", {})
    competitors = analysis_summary.get("competitors", [])
    keywords = analysis_summary.get("keyword_summary", {})

    return {
      "market_summary": (
        f"Analysis of {analysis_summary.get('listing_count', 0)} listings in the "
        f"{analysis_summary.get('platform', 'marketplace')} niche '{analysis_summary.get('input_value', '')}'."
      ),
      "competitor_summary": (
        f"Top competitor: {competitors[0]['competitor_name'] if competitors else 'N/A'} "
        f"with {competitors[0]['product_count'] if competitors else 0} products."
      ),
      "pricing_summary": (
        f"Prices range ${pricing.get('min_price', 0)}-${pricing.get('max_price', 0)}, "
        f"median ${pricing.get('median_price', 0)}."
      ),
      "keyword_opportunities": keywords.get("missing_opportunities", []),
      "risks": [
        "High competition in generic minimalist wall art",
        "Price compression at budget tier",
        "Differentiation needed via style and material specificity",
      ],
    }
