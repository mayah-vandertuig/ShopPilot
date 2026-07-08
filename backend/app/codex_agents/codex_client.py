"""Codex client supporting subprocess and MCP-ready modes."""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from app.config import get_settings
from app.codex_agents.prompts import (
  ADAPTER_REPAIR_PROMPT,
  EXTRACTION_QA_PROMPT,
  REPO_MAINTAINER_PROMPT,
  TEST_GENERATOR_PROMPT,
)

logger = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class CodexClient:
  def __init__(self):
    self.settings = get_settings()

  @property
  def is_enabled(self) -> bool:
    return self.settings.codex_agents_enabled

  def status_message(self) -> str:
    if not self.is_enabled:
      return "Codex agents are disabled. Set CODEX_AGENTS_ENABLED=true to enable."
    return f"Codex agents enabled in {self.settings.codex_mode} mode."

  def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not self.is_enabled:
      return {
        "success": False,
        "enabled": False,
        "message": "Codex agents are disabled.",
        "output": "",
      }

    if self.settings.codex_mode == "mcp":
      return self._run_mcp_placeholder(prompt, context)

    return self._run_subprocess(prompt, context)

  def _run_subprocess(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    full_prompt = prompt
    if context:
      safe_context = {k: v for k, v in context.items() if "key" not in k.lower() and "secret" not in k.lower()}
      full_prompt += f"\n\nContext:\n{json.dumps(safe_context, default=str)[:4000]}"

    try:
      result = subprocess.run(
        ["codex", "exec", "--full-auto", full_prompt],
        capture_output=True,
        text=True,
        timeout=self.settings.codex_timeout_seconds,
        cwd=str(REPO_ROOT),
      )
      output = result.stdout or result.stderr or ""
      if result.returncode != 0 and not output:
        output = self._generate_offline_response(prompt, context)

      patch_path = None
      if self.settings.codex_allow_file_patch and output:
        patch_dir = REPO_ROOT / "patches"
        patch_dir.mkdir(exist_ok=True)
        patch_path = patch_dir / f"codex_patch_{hash(prompt) % 100000}.txt"
        patch_path.write_text(output)

      return {
        "success": True,
        "enabled": True,
        "message": "Codex subprocess completed.",
        "output": output,
        "patch_path": str(patch_path) if patch_path else None,
        "require_human_review": self.settings.codex_require_human_review,
      }
    except FileNotFoundError:
      return {
        "success": True,
        "enabled": True,
        "message": "Codex CLI not found. Returning structured offline analysis.",
        "output": self._generate_offline_response(prompt, context),
        "require_human_review": True,
      }
    except subprocess.TimeoutExpired:
      return {
        "success": False,
        "enabled": True,
        "message": f"Codex timed out after {self.settings.codex_timeout_seconds}s.",
        "output": "",
      }
    except Exception as e:
      logger.warning("Codex subprocess error: %s", e)
      return {
        "success": False,
        "enabled": True,
        "message": str(e),
        "output": self._generate_offline_response(prompt, context),
      }

  def _run_mcp_placeholder(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """MCP-ready structure. Full MCP orchestration not yet implemented."""
    return {
      "success": True,
      "enabled": True,
      "message": "MCP mode is structured but not fully implemented. Use CODEX_MODE=subprocess.",
      "output": self._generate_offline_response(prompt, context),
      "mcp_ready": True,
      "require_human_review": True,
    }

  def _generate_offline_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
    return json.dumps({
      "diagnosis": "Offline Codex analysis — review adapter selectors and HTML structure.",
      "proposed_patch": "# Review adapter parse_listings() selectors against current page HTML",
      "test_plan": "Add fixture HTML test in backend/tests/",
      "risk_notes": "Human review required before applying any patch.",
      "prompt_summary": prompt[:200],
    }, indent=2)

  def repair_adapter(self, platform: str, failing_url: str, html_sample: str, error: str, adapter_path: str) -> Dict[str, Any]:
    prompt = ADAPTER_REPAIR_PROMPT.format(
      platform=platform, failing_url=failing_url, error_message=error
    )
    return self.run(prompt, {
      "platform": platform,
      "html_sample_length": len(html_sample),
      "adapter_file_path": adapter_path,
    })

  def extraction_qa(self, platform: str, raw_content: str, parsed_listings: list) -> Dict[str, Any]:
    prompt = EXTRACTION_QA_PROMPT.format(platform=platform)
    return self.run(prompt, {
      "platform": platform,
      "raw_content_length": len(raw_content),
      "parsed_count": len(parsed_listings),
      "parsed_listings": parsed_listings[:3],
    })

  def generate_tests(self, target_file: str, behavior: str) -> Dict[str, Any]:
    prompt = TEST_GENERATOR_PROMPT.format(target_file=target_file, behavior_description=behavior)
    return self.run(prompt, {"target_file": target_file, "behavior": behavior})

  def maintain_repo(self, repo_summary: dict) -> Dict[str, Any]:
    return self.run(REPO_MAINTAINER_PROMPT, repo_summary)
