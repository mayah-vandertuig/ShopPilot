"""Tests for AI service helpers."""

from app.services.ai import _normalize_confidence, _normalize_string_list, _parse_json_from_llm


def test_parse_json_from_llm_strips_markdown_fence():
  raw = '```json\n{"recommendations": [{"category": "title"}]}\n```'
  parsed = _parse_json_from_llm(raw)
  assert parsed["recommendations"][0]["category"] == "title"


def test_normalize_confidence_accepts_percent_strings():
  assert _normalize_confidence("85%") == 0.85
  assert _normalize_confidence(85) == 0.85
  assert _normalize_confidence(0.6) == 0.6


def test_normalize_string_list_handles_mixed_shapes():
  assert _normalize_string_list("one") == ["one"]
  assert _normalize_string_list([{"text": "evidence"}]) == ["evidence"]
