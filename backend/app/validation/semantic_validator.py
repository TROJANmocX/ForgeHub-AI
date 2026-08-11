"""
ForgeHub AI — Semantic Validator
Detects logically invalid operations based on column semantic types.
Catches currency mixing, percentage aggregation, identifier arithmetic, etc.
"""
from __future__ import annotations

import re

from app.models.artifacts import ValidationCheck, ValidationReport
from app.models.metadata import DatasetMetadata

# Semantic type groups
_CURRENCY_TYPES = {"currency_usd", "currency_eur", "currency_gbp", "currency"}
_PERCENTAGE_TYPES = {"percentage", "rate", "ratio"}
_IDENTIFIER_TYPES = {"identifier"}
_QUANTITY_TYPES = {"quantity"}


class SemanticValidator:
    """
    Validates semantic correctness of SQL expressions.
    Operates on both SQL text (pattern matching) and column metadata.
    """

    def validate(self, sql: str, dataset: DatasetMetadata) -> ValidationReport:
        checks: list[ValidationCheck] = []
        errors: list[str] = []
        warnings: list[str] = []

        col_map = dataset.column_map()

        # ── Rule 1: Mixed-currency addition ──────────────────────────────────
        currency_cols = [
            c.name for c in dataset.columns
            if c.semantic_type in _CURRENCY_TYPES
        ]
        # Check if multiple distinct currency types are summed together
        currency_types_present = {
            c.semantic_type for c in dataset.columns
            if c.semantic_type in _CURRENCY_TYPES
        }
        if len(currency_types_present) > 1:
            error = (
                f"SEMANTIC_ERROR: Mixed-currency addition detected. "
                f"Columns with different currency types cannot be added: {currency_types_present}"
            )
            errors.append(error)
            checks.append(ValidationCheck(name="Currency Safety", passed=False, message=error))
        else:
            checks.append(ValidationCheck(name="Currency Safety", passed=True))

        # ── Rule 2: SUM of percentage columns ─────────────────────────────────
        pct_col_names = [
            c.name for c in dataset.columns
            if c.semantic_type in _PERCENTAGE_TYPES
        ]
        pct_sum_errors: list[str] = []
        for col_name in pct_col_names:
            # Look for SUM(col_name) pattern in SQL (case-insensitive)
            pattern = re.compile(
                rf"\bSUM\s*\(\s*{re.escape(col_name)}\s*\)",
                re.IGNORECASE,
            )
            if pattern.search(sql):
                pct_sum_errors.append(
                    f"SEMANTIC_ERROR: SUM({col_name}) is invalid — "
                    f"'{col_name}' is a {col_map[col_name].semantic_type}. "
                    f"Use AVG() instead."
                )

        if pct_sum_errors:
            errors.extend(pct_sum_errors)
            checks.append(
                ValidationCheck(
                    name="Percentage Aggregation",
                    passed=False,
                    message="; ".join(pct_sum_errors),
                )
            )
        else:
            checks.append(ValidationCheck(name="Percentage Aggregation", passed=True))

        # ── Rule 3: Identifier used in arithmetic ─────────────────────────────
        id_col_names = [
            c.name for c in dataset.columns
            if c.semantic_type in _IDENTIFIER_TYPES
        ]
        id_arith_errors: list[str] = []
        arith_funcs = re.compile(r"\b(SUM|AVG|MIN\s*\+|MAX\s*\+)\s*\(", re.IGNORECASE)
        for col_name in id_col_names:
            # Check if identifier appears inside arithmetic aggregate
            pattern = re.compile(
                rf"\b(?:SUM|AVG)\s*\(\s*{re.escape(col_name)}\s*\)",
                re.IGNORECASE,
            )
            if pattern.search(sql):
                id_arith_errors.append(
                    f"SEMANTIC_ERROR: Arithmetic on identifier column '{col_name}' is invalid."
                )

        if id_arith_errors:
            errors.extend(id_arith_errors)
            checks.append(
                ValidationCheck(
                    name="Identifier Safety",
                    passed=False,
                    message="; ".join(id_arith_errors),
                )
            )
        else:
            checks.append(ValidationCheck(name="Identifier Safety", passed=True))

        # ── Rule 4: Undefined currency warning ────────────────────────────────
        undefined_currency = [
            c.name for c in dataset.columns
            if c.semantic_type is None
            and any(kw in c.name.lower() for kw in ("price", "revenue", "amount", "cost", "value"))
        ]
        if undefined_currency:
            msg = f"UNDEFINED_CURRENCY warning: {undefined_currency} — currency unit not in metadata."
            warnings.append(msg)
            checks.append(ValidationCheck(name="Currency Definition", passed=False, message=msg))
        else:
            checks.append(ValidationCheck(name="Currency Definition", passed=True))

        passed = len(errors) == 0
        return ValidationReport(passed=passed, checks=checks, errors=errors, warnings=warnings)
