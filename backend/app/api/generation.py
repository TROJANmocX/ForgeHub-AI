"""ForgeHub AI — Generation API route."""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.generation_agent import GenerationAgent
from app.agents.metadata_agent import MetadataAgent
from app.agents.quality_agent import QualityAgent
from app.agents.reasoning_agent import ReasoningAgent
from app.config import get_settings
from app.datahub.metadata import build_symbol_table
from app.llm.mock import MockProvider
from app.models.artifacts import GeneratedArtifact, ValidationCheck, ValidationReport
from app.models.generation import GenerationRequest, GenerationStatus
from app.validation.semantic_validator import SemanticValidator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/generate", tags=["generation"])

_metadata_agent = MetadataAgent()
_quality_agent = QualityAgent()
_reasoning_agent = ReasoningAgent()
_semantic_validator = SemanticValidator()

# In-memory run store (production would use a DB)
_runs: dict[str, dict] = {}


class ProvenanceResponse(BaseModel):
    decision: str
    expression: Optional[str]
    evidence: list[dict]
    confidence: float


class ValidationCheckResponse(BaseModel):
    name: str
    passed: bool
    message: Optional[str] = None


class ValidationReportResponse(BaseModel):
    passed: bool
    checks: list[ValidationCheckResponse]
    errors: list[str]
    warnings: list[str]


class ReasoningTransformResponse(BaseModel):
    name: str
    expression: str
    reason: str
    confidence: float


from pydantic import BaseModel, ConfigDict


class ReasoningPlanResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    grain: str
    source_tables: list[str]
    transformations: list[ReasoningTransformResponse]
    tests: list[str]
    assumptions: list[dict]
    metadata_gaps: list[str]


class GenerationResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    run_id: str
    dataset_id: str
    status: str
    model_name: str
    sql: str
    schema_yml: str
    readme: str
    provenance: list[ProvenanceResponse]
    validation: ValidationReportResponse
    reasoning_plan: ReasoningPlanResponse
    repair_attempts: int
    llm_provider: str
    blocking_gaps: list[str]


def _get_llm_provider(dataset_id: str, broken: bool):
    settings = get_settings()
    provider_name = settings.llm_provider

    if provider_name == "mock" or settings.demo_mode:
        return MockProvider(dataset_id=dataset_id, broken=broken)

    if provider_name == "anthropic":
        from app.llm.claude import ClaudeProvider
        return ClaudeProvider(api_key=settings.anthropic_api_key)
    if provider_name == "openai":
        from app.llm.openai import OpenAIProvider
        return OpenAIProvider(api_key=settings.openai_api_key)
    if provider_name == "gemini":
        from app.llm.gemini import GeminiProvider
        return GeminiProvider(api_key=settings.gemini_api_key)

    return MockProvider(dataset_id=dataset_id, broken=broken)


@router.post("", response_model=GenerationResponse)
def generate(request: GenerationRequest):
    """
    Run the full ForgeHub AI pipeline:
    metadata → quality → reasoning → generate → validate → artifact
    """
    # ── Fetch metadata ────────────────────────────────────────────────────────
    try:
        dataset = _metadata_agent.fetch(request.dataset_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Dataset '{request.dataset_id}' not found")

    # ── Quality gate ──────────────────────────────────────────────────────────
    quality_report = _quality_agent.score(dataset)
    blocking_gap_msgs = [g.reason for g in quality_report.blocking_gaps]

    # ── Symbol table ──────────────────────────────────────────────────────────
    symbol_table = _metadata_agent.get_symbol_table(dataset)

    # ── Reasoning plan ────────────────────────────────────────────────────────
    plan = _reasoning_agent.build_plan(dataset, model_name_override=request.model_name)

    # ── LLM + generation ──────────────────────────────────────────────────────
    llm = _get_llm_provider(request.dataset_id, broken=request.broken_mode)
    agent = GenerationAgent(llm=llm)
    artifact = agent.generate(dataset=dataset, plan=plan, symbol_table=symbol_table)

    # ── Semantic validation (post-generation) ─────────────────────────────────
    sem_report = _semantic_validator.validate(sql=artifact.sql, dataset=dataset)

    # ── Merge validation reports ──────────────────────────────────────────────
    combined_checks = (artifact.validation_report.checks if artifact.validation_report else []) + sem_report.checks
    combined_errors = (artifact.validation_report.errors if artifact.validation_report else []) + sem_report.errors
    combined_warnings = (artifact.validation_report.warnings if artifact.validation_report else []) + sem_report.warnings
    
    artifact_passed = artifact.validation_report.passed if artifact.validation_report else False
    has_sql = bool(artifact.sql and artifact.sql.strip())
    combined_passed = artifact_passed and has_sql and sem_report.passed

    # ── Status determination ──────────────────────────────────────────────────
    if not combined_passed:
        status = GenerationStatus.FAILED
    elif blocking_gap_msgs:
        status = GenerationStatus.REQUIRES_REVIEW
    else:
        status = GenerationStatus.VALIDATED


    # ── Store run ─────────────────────────────────────────────────────────────
    _runs[artifact.run_id] = {
        "artifact": artifact,
        "status": status,
        "blocking_gaps": blocking_gap_msgs,
    }

    return GenerationResponse(
        run_id=artifact.run_id,
        dataset_id=artifact.dataset_id,
        status=status.value,
        model_name=artifact.model_name,
        sql=artifact.sql,
        schema_yml=artifact.schema_yml,
        readme=artifact.readme,
        provenance=[
            ProvenanceResponse(
                decision=p.decision,
                expression=p.expression,
                evidence=p.evidence,
                confidence=p.confidence,
            )
            for p in artifact.provenance
        ],
        validation=ValidationReportResponse(
            passed=combined_passed,
            checks=[
                ValidationCheckResponse(name=c.name, passed=c.passed, message=c.message)
                for c in combined_checks
            ],
            errors=combined_errors,
            warnings=combined_warnings,
        ),
        reasoning_plan=ReasoningPlanResponse(
            model_name=plan.model_name,
            grain=plan.grain,
            source_tables=plan.source_tables,
            transformations=[
                ReasoningTransformResponse(
                    name=t.name,
                    expression=t.expression,
                    reason=t.reason,
                    confidence=t.confidence,
                )
                for t in plan.transformations
            ],
            tests=plan.tests,
            assumptions=[a.model_dump() for a in plan.assumptions],
            metadata_gaps=plan.metadata_gaps,
        ),
        repair_attempts=artifact.repair_attempts,
        llm_provider=artifact.llm_provider,
        blocking_gaps=blocking_gap_msgs,
    )


@router.get("/runs/{run_id}")
def get_run(run_id: str):
    """Get status of a generation run."""
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return {
        "run_id": run_id,
        "status": run["status"].value,
        "blocking_gaps": run["blocking_gaps"],
    }
