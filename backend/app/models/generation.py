"""ForgeHub AI — Pydantic models for generation requests and run tracking."""
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GenerationStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class GenerationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    dataset_id: str  # DataHub URN or fixture key (e.g. "orders")
    model_name: Optional[str] = None  # override generated model name
    broken_mode: bool = False  # trigger hallucination failure demo



class GenerationRun(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dataset_id: str
    status: GenerationStatus = GenerationStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    repair_attempts: int = 0
    error_messages: list[str] = Field(default_factory=list)
    blocking_gaps: list[str] = Field(default_factory=list)
