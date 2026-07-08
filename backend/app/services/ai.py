"""OpenAI product intelligence service."""

import json
import logging
import re
from typing import Any, Dict, List

from app.config import get_settings
from app.exceptions import IngestionError

logger = logging.getLogger(__name__)


def _parse_json_from_llm(text: str) -> Any:
  cleaned = text.strip()
  if cleaned.startswith("```"):
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
  return json.loads(cleaned)


def _normalize_confidence(value: Any) -> float:
  if value is None:
    return 0.7
  if isinstance(value, str):
    value = value.strip().rstrip("%")
    if not value:
      return 0.7
    value = float(value)
  confidence = float(value)
  if confidence > 1:
    confidence /= 100.0
  return max(0.0, min(1.0, confidence))


def _normalize_string_list(value: Any) -> List[str]:
  if not value:
    return []
  if isinstance(value, str):
    return [value]
  if isinstance(value, list):
    items: List[str] = []
    for item in value:
      if isinstance(item, str):
        items.append(item)
      elif isinstance(item, dict):
        text = item.get("text") or item.get("evidence") or item.get("detail")
        if text:
          items.append(str(text))
      else:
        items.append(str(item))
    return items
  return [str(value)]


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

  def _chat(self, system: str, user: str, *, json_mode: bool = True) -> str:
    client = self._client()
    kwargs: Dict[str, Any] = {
      "model": "gpt-4o-mini",
      "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
      ],
      "temperature": 0.3,
    }
    if json_mode:
      kwargs["response_format"] = {"type": "json_object"}

    try:
      response = client.chat.completions.create(**kwargs)
      content = response.choices[0].message.content
      if not content:
        raise IngestionError("OpenAI returned an empty response")
      return content
    except IngestionError:
      raise
    except Exception as e:
      logger.warning("OpenAI chat failed: %s", e)
      raise IngestionError(f"OpenAI request failed: {e}") from e

  def _normalize_recommendation(self, item: Dict[str, Any]) -> Dict[str, Any]:
    return {
      "category": str(item.get("category") or "general"),
      "recommendation": str(
        item.get("recommendation") or item.get("text") or item.get("suggestion") or ""
      ).strip(),
      "reasoning": str(item.get("reasoning") or item.get("explanation") or "").strip(),
      "confidence": _normalize_confidence(item.get("confidence")),
    }

  def generate_listing_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not context.get("listings"):
      raise IngestionError("No listing data available for AI recommendations.")

    system = (
      "You are ShopPilot Listing Advisor. Ground all recommendations ONLY in the provided marketplace data. "
      "Do not invent competitor facts. "
      'Return JSON: {"recommendations":[{"category":"title|tags|pricing|positioning|listing|product_expansion|general",'
      '"recommendation":"...", "reasoning":"...", "confidence":0.0-1.0}]} '
      "Provide 4-6 actionable recommendations."
    )
    user = f"Analyze and recommend improvements:\n{json.dumps(context, default=str)[:12000]}"
    result = self._chat(system, user)
    try:
      parsed = _parse_json_from_llm(result)
      if isinstance(parsed, list):
        raw_items = parsed
      elif isinstance(parsed, dict) and isinstance(parsed.get("recommendations"), list):
        raw_items = parsed["recommendations"]
      else:
        raise ValueError("unexpected shape")
      recommendations = [
        self._normalize_recommendation(item)
        for item in raw_items
        if isinstance(item, dict) and self._normalize_recommendation(item)["recommendation"]
      ]
      if recommendations:
        return recommendations
    except (json.JSONDecodeError, ValueError, TypeError):
      pass

    return [{
      "category": "listing",
      "recommendation": result[:500],
      "reasoning": "AI analysis based on your collected marketplace data.",
      "confidence": 0.7,
    }]

  def ask_freeform(self, context: Dict[str, Any], question: str) -> Dict[str, Any]:
    if not context.get("listings"):
      raise IngestionError("No listing data available to answer this question.")

    system = (
      "You are ShopPilot Market Research assistant. Answer ONLY based on provided analysis data. "
      "Include uncertainty when data is insufficient. "
      'Return JSON: {"answer":"...", "supporting_evidence":["..."], "uncertainty_notes":["..."]}. '
      "supporting_evidence and uncertainty_notes must be arrays of strings."
    )
    user = f"Question: {question}\n\nData:\n{json.dumps(context, default=str)[:12000]}"
    result = self._chat(system, user)
    try:
      parsed = _parse_json_from_llm(result)
      if isinstance(parsed, dict):
        return {
          "answer": str(parsed.get("answer") or "").strip(),
          "supporting_evidence": _normalize_string_list(parsed.get("supporting_evidence")),
          "uncertainty_notes": _normalize_string_list(parsed.get("uncertainty_notes")),
        }
    except (json.JSONDecodeError, TypeError):
      pass

    return {
      "answer": result.strip(),
      "supporting_evidence": [],
      "uncertainty_notes": ["Response was not structured JSON; verify against your analysis data."],
    }
