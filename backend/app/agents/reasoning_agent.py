"""
ForgeHub AI — Reasoning Agent
Builds a structured, inspectable reasoning plan BEFORE calling the LLM.
The plan is the source of the prompt — not free-form chain-of-thought.
"""
from __future__ import annotations

from app.models.metadata import DatasetMetadata
from app.models.reasoning import (
    AssumptionRecord,
    EvidenceItem,
    ReasoningPlan,
    TransformationPlan,
)

# ─── Model name conventions ───────────────────────────────────────────────────
_MODEL_PREFIXES: dict[str, str] = {
    "orders": "fct",
    "revenue": "fct",
    "customers": "dim",
}


def _infer_model_name(dataset_name: str) -> str:
    short = dataset_name.split(".")[-1]  # "retail.orders" → "orders"
    prefix = _MODEL_PREFIXES.get(short, "fct")
    return f"{prefix}_{short}"


def _infer_grain(dataset: DatasetMetadata) -> str:
    pk_cols = [c for c in dataset.columns if c.is_primary_key]
    if pk_cols:
        keys = ", ".join(c.name for c in pk_cols)
        return f"One row per unique ({keys})"
    return "Grain not determinable from metadata — primary key undefined."


def _plan_transformations(dataset: DatasetMetadata) -> list[TransformationPlan]:
    """
    Derive safe transformations from metadata semantics.
    Only generate expressions that metadata can support.
    """
    transforms: list[TransformationPlan] = []
    col_map = dataset.column_map()

    short = dataset.name.split(".")[-1]

    if short == "orders":
        # order_value = quantity * unit_price (if both exist)
        if "quantity" in col_map and "unit_price" in col_map:
            transforms.append(
                TransformationPlan(
                    name="order_value",
                    expression="quantity * unit_price",
                    reason="Standard order value calculation: units sold × price per unit.",
                    evidence=[
                        EvidenceItem(asset=f"{dataset.name}.quantity", metadata="Quantity"),
                        EvidenceItem(asset=f"{dataset.name}.unit_price", metadata="Numeric — currency undefined"),
                    ],
                    confidence=0.85,  # lower confidence: currency unknown
                )
            )

    if short == "customers":
        if "first_name" in col_map and "last_name" in col_map:
            transforms.append(
                TransformationPlan(
                    name="full_name",
                    expression="CONCAT(first_name, ' ', last_name)",
                    reason="Derive full customer name from first and last name fields.",
                    evidence=[
                        EvidenceItem(asset=f"{dataset.name}.first_name", metadata="PII: text"),
                        EvidenceItem(asset=f"{dataset.name}.last_name", metadata="PII: text"),
                    ],
                    confidence=0.98,
                )
            )
        if "email" in col_map:
            transforms.append(
                TransformationPlan(
                    name="clean_email",
                    expression="LOWER(TRIM(email))",
                    reason="Normalize email to lowercase and strip whitespace.",
                    evidence=[
                        EvidenceItem(asset=f"{dataset.name}.email", metadata="PII: email"),
                    ],
                    confidence=0.99,
                )
            )

    if short == "revenue":
        if "gross_revenue" in col_map and "discount_amount" in col_map:
            transforms.append(
                TransformationPlan(
                    name="net_revenue",
                    expression="gross_revenue - COALESCE(discount_amount, 0)",
                    reason="Net revenue after promotional discounts.",
                    evidence=[
                        EvidenceItem(asset=f"{dataset.name}.gross_revenue", metadata="Numeric — currency ambiguous"),
                        EvidenceItem(asset=f"{dataset.name}.discount_amount", metadata="Numeric — currency ambiguous"),
                    ],
                    confidence=0.80,
                )
            )

    return transforms


def _plan_tests(dataset: DatasetMetadata) -> list[str]:
    tests: list[str] = []
    for col in dataset.columns:
        if col.is_primary_key:
            tests.append(f"{col.name}: unique")
            tests.append(f"{col.name}: not_null")
        if col.is_foreign_key:
            tests.append(f"{col.name}: not_null")
        if not col.nullable and not col.is_primary_key:
            tests.append(f"{col.name}: not_null")
    return tests


def _collect_assumptions(dataset: DatasetMetadata) -> list[AssumptionRecord]:
    assumptions: list[AssumptionRecord] = []
    for col in dataset.columns:
        if col.semantic_type is None and col.data_type in ("NUMERIC", "FLOAT", "DOUBLE"):
            assumptions.append(
                AssumptionRecord(
                    description=f"Column '{col.name}' has an undefined semantic type. Treating as a raw numeric. No currency-dependent aggregation will be performed.",
                    severity="medium",
                    metadata_gap="AMBIGUOUS_SEMANTIC_TYPE",
                )
            )
    return assumptions


class ReasoningAgent:
    """
    Produces a fully inspectable ReasoningPlan before any LLM call.
    The plan is deterministic and metadata-driven.
    """

    def build_plan(
        self,
        dataset: DatasetMetadata,
        model_name_override: str | None = None,
    ) -> ReasoningPlan:
        model_name = model_name_override or _infer_model_name(dataset.name)
        grain = _infer_grain(dataset)
        transformations = _plan_transformations(dataset)
        tests = _plan_tests(dataset)
        assumptions = _collect_assumptions(dataset)

        # Collect gap IDs from the plan itself
        gap_ids = [a.metadata_gap for a in assumptions if a.metadata_gap]

        explainability = [
            {
                "decision": t.name,
                "expression": t.expression,
                "evidence": [e.model_dump() for e in t.evidence],
                "confidence": t.confidence,
            }
            for t in transformations
        ]

        return ReasoningPlan(
            model_name=model_name,
            grain=grain,
            source_tables=[dataset.name],
            transformations=transformations,
            tests=tests,
            assumptions=assumptions,
            metadata_gaps=gap_ids,
            explainability=explainability,
        )
