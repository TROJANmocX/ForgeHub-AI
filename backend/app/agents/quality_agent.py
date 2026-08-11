"""
ForgeHub AI — Metadata Quality Agent
Scores dataset metadata 0–100 and produces an explicit gap list.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from app.models.metadata import DatasetMetadata

Severity = Literal["informational", "warning", "blocking"]


@dataclass
class MetadataGap:
    type: str  # e.g. "UNDEFINED_CURRENCY"
    asset: str  # e.g. "retail.orders.unit_price"
    severity: Severity
    reason: str
    generation_impact: str


@dataclass
class DimensionScore:
    name: str
    score: float  # 0–100
    max_score: float = 100.0


@dataclass
class MetadataQualityReport:
    dataset_name: str
    overall_score: float
    dimensions: list[DimensionScore] = field(default_factory=list)
    gaps: list[MetadataGap] = field(default_factory=list)

    @property
    def blocking_gaps(self) -> list[MetadataGap]:
        return [g for g in self.gaps if g.severity == "blocking"]

    @property
    def warning_gaps(self) -> list[MetadataGap]:
        return [g for g in self.gaps if g.severity == "warning"]

    @property
    def informational_gaps(self) -> list[MetadataGap]:
        return [g for g in self.gaps if g.severity == "informational"]


class QualityAgent:
    """
    Evaluates metadata richness and produces a transparent quality score
    with an explicit per-gap breakdown.
    """

    def score(self, dataset: DatasetMetadata) -> MetadataQualityReport:
        gaps: list[MetadataGap] = []
        dimensions: list[DimensionScore] = []

        # ── 1. Schema completeness (20 pts) ───────────────────────────────────
        has_columns = len(dataset.columns) > 0
        schema_score = 100.0 if has_columns else 0.0
        dimensions.append(DimensionScore("Schema Completeness", schema_score))

        # ── 2. Description coverage (20 pts) ─────────────────────────────────
        total_cols = len(dataset.columns)
        described_cols = sum(1 for c in dataset.columns if c.description)
        col_desc_pct = (described_cols / total_cols * 100) if total_cols else 0.0
        dataset_desc_score = 100.0 if dataset.description else 0.0
        desc_score = (col_desc_pct + dataset_desc_score) / 2
        dimensions.append(DimensionScore("Descriptions", desc_score))

        for col in dataset.columns:
            if not col.description:
                gaps.append(
                    MetadataGap(
                        type="MISSING_COLUMN_DESCRIPTION",
                        asset=f"{dataset.name}.{col.name}",
                        severity="informational",
                        reason=f"Column '{col.name}' has no description.",
                        generation_impact="AI must infer meaning from column name alone.",
                    )
                )

        if not dataset.description:
            gaps.append(
                MetadataGap(
                    type="MISSING_DATASET_DESCRIPTION",
                    asset=dataset.name,
                    severity="warning",
                    reason="Dataset has no description.",
                    generation_impact="Documentation quality will be reduced.",
                )
            )

        # ── 3. Glossary term coverage (15 pts) ────────────────────────────────
        glossary_cols = sum(1 for c in dataset.columns if c.glossary_terms)
        glossary_pct = (glossary_cols / total_cols * 100) if total_cols else 0.0
        dimensions.append(DimensionScore("Glossary Coverage", glossary_pct))

        for col in dataset.columns:
            if not col.glossary_terms:
                gaps.append(
                    MetadataGap(
                        type="MISSING_GLOSSARY_TERM",
                        asset=f"{dataset.name}.{col.name}",
                        severity="informational",
                        reason=f"Column '{col.name}' has no glossary terms.",
                        generation_impact="Semantic type validation may be limited.",
                    )
                )

        # ── 4. Lineage (10 pts) ───────────────────────────────────────────────
        has_lineage = bool(dataset.upstream_datasets or dataset.downstream_datasets)
        lineage_score = 100.0 if has_lineage else 0.0
        dimensions.append(DimensionScore("Lineage", lineage_score))

        if not has_lineage:
            gaps.append(
                MetadataGap(
                    type="MISSING_LINEAGE",
                    asset=dataset.name,
                    severity="informational",
                    reason="No upstream or downstream lineage defined.",
                    generation_impact="Cannot automatically validate source relationships.",
                )
            )

        # ── 5. Governance (15 pts) ────────────────────────────────────────────
        governance_checks = [
            bool(dataset.owners),
            bool(dataset.domains),
            any(c.pii for c in dataset.columns) or "pii" not in " ".join(dataset.tags),
        ]
        governance_score = sum(governance_checks) / len(governance_checks) * 100
        dimensions.append(DimensionScore("Governance", governance_score))

        if not dataset.owners:
            gaps.append(
                MetadataGap(
                    type="MISSING_OWNER",
                    asset=dataset.name,
                    severity="warning",
                    reason="No dataset owner defined.",
                    generation_impact="Cannot attribute governance responsibilities.",
                )
            )

        if not dataset.domains:
            gaps.append(
                MetadataGap(
                    type="MISSING_DOMAIN",
                    asset=dataset.name,
                    severity="warning",
                    reason="No domain assignment.",
                    generation_impact="Dataset cannot be categorized in the catalog.",
                )
            )

        # ── 6. Semantic metadata (20 pts) ─────────────────────────────────────
        semantic_cols = sum(1 for c in dataset.columns if c.semantic_type)
        semantic_pct = (semantic_cols / total_cols * 100) if total_cols else 0.0
        dimensions.append(DimensionScore("Semantic Metadata", semantic_pct))

        for col in dataset.columns:
            if col.semantic_type is None:
                # Heuristic: numeric columns with price/revenue/amount in name
                name_lower = col.name.lower()
                if any(kw in name_lower for kw in ("price", "revenue", "amount", "cost", "value")):
                    gaps.append(
                        MetadataGap(
                            type="UNDEFINED_CURRENCY",
                            asset=f"{dataset.name}.{col.name}",
                            severity="blocking",
                            reason=f"Column '{col.name}' appears to be a monetary value but has no currency unit defined.",
                            generation_impact="Cannot safely perform financial aggregation. Generation blocked.",
                        )
                    )
                elif col.data_type in ("NUMERIC", "FLOAT", "DOUBLE"):
                    gaps.append(
                        MetadataGap(
                            type="AMBIGUOUS_SEMANTIC_TYPE",
                            asset=f"{dataset.name}.{col.name}",
                            severity="warning",
                            reason=f"Numeric column '{col.name}' has no semantic type.",
                            generation_impact="Aggregation safety cannot be guaranteed.",
                        )
                    )

            # PII detection
            if col.pii and "pii" not in dataset.tags:
                gaps.append(
                    MetadataGap(
                        type="MISSING_PII_CLASSIFICATION",
                        asset=f"{dataset.name}.{col.name}",
                        severity="warning",
                        reason=f"Column '{col.name}' is marked PII but the dataset tag is missing.",
                        generation_impact="Generated models should mask or exclude PII fields.",
                    )
                )

        # ── Aggregate score ───────────────────────────────────────────────────
        weights = [0.20, 0.20, 0.15, 0.10, 0.15, 0.20]
        overall = sum(d.score * w for d, w in zip(dimensions, weights))

        return MetadataQualityReport(
            dataset_name=dataset.name,
            overall_score=round(overall, 1),
            dimensions=dimensions,
            gaps=gaps,
        )
