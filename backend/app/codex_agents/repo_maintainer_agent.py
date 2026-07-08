"""Repository maintainer Codex agent."""

from pathlib import Path
from typing import Any, Dict

from app.codex_agents.codex_client import CodexClient

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class RepoMaintainerAgent:
  def __init__(self):
    self.client = CodexClient()

  def review(self) -> Dict[str, Any]:
    summary = {
      "backend_files": len(list((REPO_ROOT / "app").rglob("*.py"))),
      "test_files": len(list((REPO_ROOT / "tests").rglob("*.py"))),
      "has_readme": (REPO_ROOT.parent / "README.md").exists(),
      "has_docs": (REPO_ROOT.parent / "docs").exists(),
    }

    if not self.client.is_enabled:
      return {
        "success": False,
        "enabled": False,
        "message": "Codex agents are disabled.",
        "checklist": self._offline_checklist(summary),
      }

    result = self.client.maintain_repo(summary)
    return {
      "success": True,
      "enabled": True,
      "message": result.get("message", ""),
      "checklist": self._offline_checklist(summary),
      "recommended_fixes": [
        "Ensure all adapters have corresponding tests",
        "Keep .env.example in sync with config.py",
        "Update roadmap as platforms are implemented",
      ],
    }

  def _offline_checklist(self, summary: dict) -> list:
    return [
      {"item": "Backend Python files", "status": "ok" if summary["backend_files"] > 10 else "warn", "detail": str(summary["backend_files"])},
      {"item": "Test files", "status": "ok" if summary["test_files"] >= 5 else "warn", "detail": str(summary["test_files"])},
      {"item": "README present", "status": "ok" if summary["has_readme"] else "fail"},
      {"item": "Docs folder", "status": "ok" if summary["has_docs"] else "fail"},
    ]
