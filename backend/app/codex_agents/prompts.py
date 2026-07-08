"""Codex agent prompts."""

ADAPTER_REPAIR_PROMPT = """Diagnose a failed marketplace extraction.
Platform: {platform}
Failing URL: {failing_url}
Error: {error_message}
Analyze the adapter and HTML sample. Suggest parser fixes and tests.
Do NOT include secrets. Return structured diagnosis, proposed patch, test plan, risk notes."""

EXTRACTION_QA_PROMPT = """Evaluate extraction quality for platform {platform}.
Check parsed listings against raw content. Score quality, find missing fields, suggest improvements."""

TEST_GENERATOR_PROMPT = """Generate pytest tests for file {target_file}.
Behavior: {behavior_description}
Follow existing test patterns in backend/tests/."""

REPO_MAINTAINER_PROMPT = """Review ShopPilot repository quality.
Check imports, docs, tests, setup. Return checklist and recommended fixes."""
