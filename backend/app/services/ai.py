"""OpenAI product intelligence service."""

import json
import logging
from typing import Any, Dict, List, Optional

from app.config import get_settings
from app.exceptions import IngestionError

logger = logging.getLogger(__name__)


class AIService:
  def __init__(self):
    self.settings = get_settings()

  def _require_openai(self):
    if not self.settings.has_openai:
      raise IngestionError("OPENAI_API_KEY is not configured. AI features require a valid OpenAI API key.")

  def _client(self):
    self._require_openai()
    try:
      from openai import OpenAI
      return OpenAI(api_key=self.settings.openai_api_key)
    except Exception as e:
      logger.warning("OpenAI client init failed: %s", e)
      raise IngestionError(f"OpenAI client failed to initialize: {e}") from e

  def _chat(self, system: str, user: str) -> str:
    client = self._client()
    try:
      response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
          {"role": "system", "content": system},
          {"role": "user", "content": user},
        ],
        temperature=0.3,
      )
      content = response.choices[0].message.content
      if not content:
        raise IngestionError("OpenAI returned an empty response")
      return content
    except IngestionError:
      raise
    except Exception as e:
      logger.warning("OpenAI chat failed: %s", e)
      raise IngestionError(f"OpenAI request failed: {e}") from e

  def generate_listing_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    system = (
      "You are ShopPilot Listing Advisor. Ground all recommendations ONLY in the provided marketplace data. "
      "Do not invent competitor facts. Return JSON array of recommendations with category, recommendation, reasoning, confidence."
    )
    user = f"Analyze and recommend improvements:\n{json.dumps(context, default=str)[:8000]}"
    result = self._chat(system, user)
    try:
      parsed = json.loads(result)
      if isinstance(parsed, list):
        return parsed
      if isinstance(parsed, dict) and "recommendations" in parsed:
        return parsed["recommendations"]
    except json.JSONDecodeError:
      return [{"category": "listing", "recommendation": result[:500], "reasoning": "AI analysis", "confidence": 0.7}]
    raise IngestionError("OpenAI returned an unexpected recommendations format")

  def ask_freeform(self, context: Dict[str, Any], question: str) -> Dict[str, Any]:
    system = (
      "You are ShopPilot Market Research assistant. Answer ONLY based on provided analysis data. "
      "Include uncertainty when data is insufficient. Return JSON with answer, supporting_evidence, uncertainty_notes."
    )
    user = f"Question: {question}\n\nData:\n{json.dumps(context, default=str)[:8000]}"
    result = self._chat(system, user)
    try:
      return json.loads(result)
    except json.JSONDecodeError:
      return {"answer": result, "supporting_evidence": [], "uncertainty_notes": []}
