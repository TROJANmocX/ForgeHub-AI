"""ForgeHub AI — Pydantic models for generated artifacts and provenance."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProvenanceDecision(BaseModel):
    decision: str
    expression: Optional[str] = None
    evidence: list[dict] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class ValidationCheck(BaseModel):
    name: str
    passed: bool
    message: Optional[str] = None


class ValidationReport(BaseModel):
    passed: bool
    checks: list[ValidationCheck] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class GeneratedArtifact(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    run_id: str
    dataset_id: str
    model_name: str
    sql: str
    schema_yml: str
    readme: str
    provenance: list[ProvenanceDecision] = Field(default_factory=list)
    validation_report: Optional[ValidationReport] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    llm_provider: str = "mock"
    repair_attempts: int = 0
