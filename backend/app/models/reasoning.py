"""ForgeHub AI — Pydantic models for structured reasoning."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EvidenceItem(BaseModel):
    asset: str  # e.g. "retail.orders.quantity"
    metadata: str  # e.g. "Quantity"


class TransformationPlan(BaseModel):
    name: str
    expression: str
    reason: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class AssumptionRecord(BaseModel):
    description: str
    severity: str  # "low" | "medium" | "high"
    metadata_gap: Optional[str] = None


class ReasoningPlan(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    grain: str
    source_tables: list[str]
    transformations: list[TransformationPlan] = Field(default_factory=list)
    tests: list[str] = Field(default_factory=list)
    assumptions: list[AssumptionRecord] = Field(default_factory=list)
    metadata_gaps: list[str] = Field(default_factory=list)
    explainability: list[dict] = Field(default_factory=list)

