# Codex Engineering Agents

Codex agents are **optional developer tools** for maintaining marketplace extractors. They are **not** part of the seller workflow.

## Environment Controls

| Variable | Default | Description |
|----------|---------|-------------|
| `CODEX_AGENTS_ENABLED` | `false` | Enable Codex workflows |
| `CODEX_MODE` | `subprocess` | `subprocess` or `mcp` (MCP-ready placeholder) |
| `CODEX_ALLOW_FILE_PATCH` | `false` | Allow writing patch files |
| `CODEX_REQUIRE_HUMAN_REVIEW` | `true` | Require human review before applying |
| `CODEX_TIMEOUT_SECONDS` | `120` | Subprocess timeout |

## Agents

### AdapterRepairAgent
Diagnose failed extraction, suggest parser fixes, generate patches and tests.

### ExtractionQAAgent
Evaluate extraction quality, find missing fields, recommend improvements.

### TestGeneratorAgent
Generate pytest tests for adapters and analysis modules.

### RepoMaintainerAgent
Review repo quality, find broken imports, weak docs/tests.

## Safety Rules

- Never required for normal app use or tests
- Never expose secrets to Codex prompts
- Never auto-apply patches unless `CODEX_ALLOW_FILE_PATCH=true`
- Always save output as reviewable recommendations

## Enabling

```bash
CODEX_AGENTS_ENABLED=true
CODEX_MODE=subprocess
# Optional: CODEX_ALLOW_FILE_PATCH=true
```

## MCP-Ready Mode

`CODEX_MODE=mcp` structures the client for future MCP tool integration. Full MCP orchestration is not yet implemented — subprocess mode is the supported path.
