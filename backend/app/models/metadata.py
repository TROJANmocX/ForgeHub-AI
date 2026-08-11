"""ForgeHub AI — Pydantic models for DataHub metadata."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ColumnMetadata(BaseModel):
    """Strongly-typed representation of a single dataset column."""

    name: str
    data_type: str
    description: Optional[str] = None
    glossary_terms: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    nullable: Optional[bool] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    semantic_type: Optional[str] = None  # e.g. "currency_usd", "percentage", "identifier"
    pii: bool = False


class DatasetMetadata(BaseModel):
    """Strongly-typed representation of a DataHub dataset entity."""

    urn: str
    name: str
    platform: str
    environment: str
    description: Optional[str] = None
    columns: list[ColumnMetadata] = Field(default_factory=list)
    owners: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    glossary_terms: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    upstream_datasets: list[str] = Field(default_factory=list)
    downstream_datasets: list[str] = Field(default_factory=list)
    custom_properties: dict[str, str] = Field(default_factory=dict)

    # ─── Symbol table helper ──────────────────────────────────────────────────
    def column_names(self) -> set[str]:
        return {col.name for col in self.columns}

    def column_map(self) -> dict[str, ColumnMetadata]:
        return {col.name: col for col in self.columns}
