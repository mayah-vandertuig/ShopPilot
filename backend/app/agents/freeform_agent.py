"""Freeform question agent."""

from typing import Any, Dict

from app.services.ai import AIService


class FreeformAgent:
  def __init__(self):
    self.ai = AIService()

  def ask(self, analysis_data: Dict[str, Any], question: str) -> Dict[str, Any]:
    result = self.ai.ask_freeform(analysis_data, question)
    return {
      "answer": result.get("answer", ""),
      "supporting_evidence": result.get("supporting_evidence", []),
      "uncertainty_notes": result.get("uncertainty_notes", []),
      "data_source": "live",
    }
