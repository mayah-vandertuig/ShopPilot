"""OpenAI product intelligence service."""

import json
import logging
from typing import Any, Dict, List, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)


class AIService:
  def __init__(self):
    self.settings = get_settings()

  def _client(self):
    if not self.settings.has_openai:
      return None
    try:
      from openai import OpenAI
      return OpenAI(api_key=self.settings.openai_api_key)
    except Exception as e:
      logger.warning("OpenAI client init failed: %s", e)
      return None

  def _chat(self, system: str, user: str) -> Optional[str]:
    client = self._client()
    if not client:
      return None
    try:
      response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
          {"role": "system", "content": system},
          {"role": "user", "content": user},
        ],
        temperature=0.3,
      )
      return response.choices[0].message.content
    except Exception as e:
      logger.warning("OpenAI chat failed: %s", e)
      return None

  def generate_listing_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    system = (
      "You are ShopPilot Listing Advisor. Ground all recommendations ONLY in the provided marketplace data. "
      "Do not invent competitor facts. Return JSON array of recommendations with category, recommendation, reasoning, confidence."
    )
    user = f"Analyze and recommend improvements:\n{json.dumps(context, default=str)[:8000]}"
    result = self._chat(system, user)
    if result:
      try:
        parsed = json.loads(result)
        if isinstance(parsed, list):
          return parsed
        if isinstance(parsed, dict) and "recommendations" in parsed:
          return parsed["recommendations"]
      except json.JSONDecodeError:
        return [{"category": "listing", "recommendation": result[:500], "reasoning": "AI analysis", "confidence": 0.7}]
    return self._mock_recommendations(context)

  def ask_freeform(self, context: Dict[str, Any], question: str) -> Dict[str, Any]:
    system = (
      "You are ShopPilot Market Research assistant. Answer ONLY based on provided analysis data. "
      "Include uncertainty when data is insufficient. Return JSON with answer, supporting_evidence, uncertainty_notes."
    )
    user = f"Question: {question}\n\nData:\n{json.dumps(context, default=str)[:8000]}"
    result = self._chat(system, user)
    if result:
      try:
        return json.loads(result)
      except json.JSONDecodeError:
        return {"answer": result, "supporting_evidence": [], "uncertainty_notes": []}
    return self._mock_freeform(question, context)

  def _mock_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
      {
        "category": "title",
        "recommendation": "Minimalist Line Art Canvas Print - Neutral Beige Abstract Wall Decor",
        "reasoning": "Top competitors use style + material + color + use-case in titles. OPENAI_API_KEY not set — showing template recommendation.",
        "confidence": 0.65,
      },
      {
        "category": "pricing",
        "recommendation": f"Price between ${context.get('pricing_summary', {}).get('suggested_min', 25)}-${context.get('pricing_summary', {}).get('suggested_max', 55)}",
        "reasoning": "Based on median competitor pricing in collected data.",
        "confidence": 0.72,
      },
      {
        "category": "tags",
        "recommendation": "minimalist wall art, line art print, neutral decor, scandinavian art, abstract canvas",
        "reasoning": "High-frequency keywords from competitor listings.",
        "confidence": 0.68,
      },
      {
        "category": "positioning",
        "recommendation": "Position as premium minimalist decor for modern living spaces",
        "reasoning": "Market shows strong demand for neutral, minimalist styles at mid-premium price points.",
        "confidence": 0.7,
      },
    ]

  def _mock_freeform(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    pricing = context.get("pricing_summary", {})
    return {
      "answer": (
        f"Based on the collected marketplace data for this analysis: "
        f"average price is ${pricing.get('average_price', 'N/A')}, "
        f"with {len(context.get('listings', []))} listings analyzed. "
        f"Regarding your question '{question}': the data suggests strong competition in minimalist wall art "
        f"with opportunities in neutral color palettes and bundled print sets. "
        f"Set OPENAI_API_KEY for AI-powered insights."
      ),
      "supporting_evidence": [
        f"Analyzed {len(context.get('listings', []))} listings",
        f"Median price: ${pricing.get('median_price', 'N/A')}",
        f"Top competitors: {', '.join(c.get('competitor_name', '') for c in context.get('competitors', [])[:3])}",
      ],
      "uncertainty_notes": ["OPENAI_API_KEY not configured — response uses data summary only."],
    }
