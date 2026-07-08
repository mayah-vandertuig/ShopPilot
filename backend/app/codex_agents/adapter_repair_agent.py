"""Adapter repair Codex agent."""

from typing import Any, Dict

from app.codex_agents.codex_client import CodexClient


class AdapterRepairAgent:
  def __init__(self):
    self.client = CodexClient()

  def repair(self, platform: str, failing_url: str, html_sample: str, error: str, adapter_path: str) -> Dict[str, Any]:
    if not self.client.is_enabled:
      return {
        "success": False,
        "enabled": False,
        "message": "Codex agents are disabled. Set CODEX_AGENTS_ENABLED=true.",
        "diagnosis": "",
        "proposed_patch": "",
        "test_plan": "",
        "risk_notes": "",
      }

    result = self.client.repair_adapter(platform, failing_url, html_sample, error, adapter_path)
    import json
    try:
      parsed = json.loads(result.get("output", "{}"))
    except json.JSONDecodeError:
      parsed = {"diagnosis": result.get("output", "")}

    return {
      "success": result.get("success", False),
      "enabled": True,
      "message": result.get("message", ""),
      "diagnosis": parsed.get("diagnosis", ""),
      "proposed_patch": parsed.get("proposed_patch", ""),
      "test_plan": parsed.get("test_plan", ""),
      "risk_notes": parsed.get("risk_notes", "Human review required."),
      "patch_path": result.get("patch_path"),
    }
