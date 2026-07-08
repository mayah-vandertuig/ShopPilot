"""Test generator Codex agent."""

from typing import Any, Dict

from app.codex_agents.codex_client import CodexClient


class TestGeneratorAgent:
  def __init__(self):
    self.client = CodexClient()

  def generate(self, target_file: str, behavior_description: str) -> Dict[str, Any]:
    if not self.client.is_enabled:
      return {
        "success": False,
        "enabled": False,
        "message": "Codex agents are disabled.",
        "test_code": "",
        "explanation": "",
      }

    result = self.client.generate_tests(target_file, behavior_description)
    test_code = f'''"""Auto-generated tests for {target_file}."""
import pytest

def test_{behavior_description.replace(" ", "_")[:30]}():
    """{behavior_description}"""
    # TODO: Implement based on Codex output
    assert True
'''
    return {
      "success": result.get("success", False),
      "enabled": True,
      "message": result.get("message", ""),
      "test_code": result.get("output", test_code),
      "explanation": f"Generated tests for {target_file}: {behavior_description}",
    }
