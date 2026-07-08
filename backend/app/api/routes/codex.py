"""Codex engineering agent API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.codex_agents.adapter_repair_agent import AdapterRepairAgent
from app.codex_agents.extraction_qa_agent import ExtractionQAAgent
from app.codex_agents.test_generator_agent import TestGeneratorAgent
from app.config import get_settings
from app.database import get_db
from app.models.database import CodexRun
from app.schemas import (
  AdapterRepairRequest,
  CodexAgentResponse,
  CodexStatusResponse,
  ExtractionQARequest,
  TestGeneratorRequest,
)

router = APIRouter(prefix="/api/codex", tags=["codex"])


@router.get("/status", response_model=CodexStatusResponse)
def codex_status():
  settings = get_settings()
  message = "Codex agents are disabled." if not settings.codex_agents_enabled else f"Codex enabled in {settings.codex_mode} mode."
  return CodexStatusResponse(
    enabled=settings.codex_agents_enabled,
    mode=settings.codex_mode,
    allow_file_patch=settings.codex_allow_file_patch,
    require_human_review=settings.codex_require_human_review,
    message=message,
  )


@router.post("/repair-adapter", response_model=CodexAgentResponse)
def repair_adapter(request: AdapterRepairRequest, db: Session = Depends(get_db)):
  settings = get_settings()
  if not settings.codex_agents_enabled:
    return CodexAgentResponse(
      success=False, enabled=False,
      message="Codex agents are disabled. Set CODEX_AGENTS_ENABLED=true to enable.",
    )

  agent = AdapterRepairAgent()
  result = agent.repair(
    request.platform, request.failing_url, request.failing_html_sample,
    request.error_message, request.adapter_file_path,
  )

  run = CodexRun(
    run_type="adapter_repair",
    platform=request.platform,
    status="completed" if result.get("success") else "failed",
    input_summary=f"{request.platform}: {request.failing_url[:100]}",
    output_summary=result.get("diagnosis", "")[:500],
    proposed_patch=result.get("proposed_patch", ""),
    applied_patch=False,
  )
  db.add(run)
  db.commit()

  return CodexAgentResponse(success=result.get("success", False), enabled=True, message=result.get("message", ""), result=result)


@router.post("/extraction-qa", response_model=CodexAgentResponse)
def extraction_qa(request: ExtractionQARequest, db: Session = Depends(get_db)):
  settings = get_settings()
  if not settings.codex_agents_enabled:
    return CodexAgentResponse(success=False, enabled=False, message="Codex agents are disabled.")

  agent = ExtractionQAAgent()
  result = agent.evaluate(request.platform, request.sample_raw_content, request.parsed_listings)

  run = CodexRun(
    run_type="extraction_qa",
    platform=request.platform,
    status="completed",
    input_summary=f"QA for {request.platform}",
    output_summary=f"Score: {result.get('extraction_score', 0)}",
  )
  db.add(run)
  db.commit()

  return CodexAgentResponse(success=result.get("success", False), enabled=True, message=result.get("message", ""), result=result)


@router.post("/generate-tests", response_model=CodexAgentResponse)
def generate_tests(request: TestGeneratorRequest, db: Session = Depends(get_db)):
  settings = get_settings()
  if not settings.codex_agents_enabled:
    return CodexAgentResponse(success=False, enabled=False, message="Codex agents are disabled.")

  agent = TestGeneratorAgent()
  result = agent.generate(request.target_file, request.behavior_description)

  run = CodexRun(
    run_type="test_generator",
    status="completed",
    input_summary=request.target_file,
    output_summary=result.get("explanation", "")[:500],
    proposed_patch=result.get("test_code", ""),
  )
  db.add(run)
  db.commit()

  return CodexAgentResponse(success=result.get("success", False), enabled=True, message=result.get("message", ""), result=result)
