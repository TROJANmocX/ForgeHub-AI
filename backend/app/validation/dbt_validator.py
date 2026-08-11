"""
ForgeHub AI — dbt YAML Validator
Validates generated schema.yml against the verified symbol table.
Catches hallucinated columns, missing descriptions, and invalid test references.
"""
from __future__ import annotations

import yaml

from app.models.artifacts import ValidationCheck, ValidationReport


class DbtValidator:
    """
    Validates schema.yml structure and column references.
    Ensures no hallucinated columns, valid test references, and proper descriptions.
    """

    def validate(
        self,
        schema_yml: str,
        symbol_table: dict[str, dict],
        model_name: str,
    ) -> ValidationReport:
        checks: list[ValidationCheck] = []
        errors: list[str] = []
        warnings: list[str] = []

        # ── 1. Parse YAML ─────────────────────────────────────────────────────
        try:
            schema = yaml.safe_load(schema_yml)
        except yaml.YAMLError as exc:
            checks.append(ValidationCheck(name="dbt YAML Parse", passed=False, message=str(exc)))
            errors.append(f"DBT_YAML_PARSE_ERROR: {exc}")
            return ValidationReport(passed=False, checks=checks, errors=errors, warnings=warnings)

        checks.append(ValidationCheck(name="dbt YAML Parse", passed=True))

        if not isinstance(schema, dict):
            checks.append(ValidationCheck(name="dbt Schema Structure", passed=False, message="schema.yml root is not a dict"))
            errors.append("DBT_SCHEMA_STRUCTURE_ERROR: Root must be a YAML dict")
            return ValidationReport(passed=False, checks=checks, errors=errors, warnings=warnings)

        # ── 2. Find the model definition ─────────────────────────────────────
        models = schema.get("models", [])
        if not models:
            checks.append(ValidationCheck(name="dbt Model Present", passed=False, message="No models defined"))
            errors.append("DBT_NO_MODEL: schema.yml has no models section")
            return ValidationReport(passed=False, checks=checks, errors=errors, warnings=warnings)

        model_def = next((m for m in models if m.get("name") == model_name), None)
        if model_def is None:
            # Try to find any model
            model_def = models[0]
            warnings.append(f"DBT_MODEL_NAME_MISMATCH: Expected '{model_name}', found '{model_def.get('name')}'")

        checks.append(ValidationCheck(name="dbt Model Present", passed=True))

        # ── 3. Column hallucination check ─────────────────────────────────────
        # Build all-known-columns from symbol table
        all_known: set[str] = set()
        for col_dict in symbol_table.values():
            all_known.update(c.lower() for c in col_dict.keys())

        # Also allow derived columns (computed in SQL) by not hard-blocking them
        # but DO block columns that are clearly not in the source
        declared_columns = model_def.get("columns", [])
        hallucinated: list[str] = []

        # Derived column names that are calculated/derived in SQL
        KNOWN_DERIVED_COLUMNS = {
            "full_name",
            "clean_email",
            "order_value",
            "net_revenue",
            "avg_discount_rate",
            "total_orders",
            "total_discounts",
            "total_gross_revenue",
            "month",
        }

        for col in declared_columns:
            col_name = col.get("name", "").lower()
            if not col_name:
                continue
            is_known = col_name in all_known
            is_derived = col_name in KNOWN_DERIVED_COLUMNS
            if not is_known and not is_derived:
                hallucinated.append(col_name)

        if hallucinated:
            msg = f"UNKNOWN_COLUMNS in schema.yml: {hallucinated}"
            errors.append(f"DBT_HALLUCINATED_COLUMNS: {hallucinated}")
            checks.append(ValidationCheck(name="Column References", passed=False, message=msg))
        else:
            checks.append(ValidationCheck(name="Column References", passed=True))

        # ── 4. Description coverage ───────────────────────────────────────────
        undescribed = [
            col.get("name")
            for col in declared_columns
            if not col.get("description")
        ]
        if undescribed:
            warnings.append(f"MISSING_DESCRIPTIONS: {undescribed}")
            checks.append(
                ValidationCheck(name="Column Descriptions", passed=False, message=f"Missing: {undescribed}")
            )
        else:
            checks.append(ValidationCheck(name="Column Descriptions", passed=True))

        # ── 5. Valid test references ───────────────────────────────────────────
        valid_tests = {"unique", "not_null", "accepted_values", "relationships"}
        invalid_tests: list[str] = []
        for col in declared_columns:
            for test in col.get("tests", []):
                test_name = test if isinstance(test, str) else list(test.keys())[0]
                if test_name not in valid_tests:
                    invalid_tests.append(f"{col.get('name')}.{test_name}")

        if invalid_tests:
            errors.append(f"DBT_INVALID_TESTS: {invalid_tests}")
            checks.append(ValidationCheck(name="Test References", passed=False, message=str(invalid_tests)))
        else:
            checks.append(ValidationCheck(name="Test References", passed=True))

        passed = len(errors) == 0
        return ValidationReport(passed=passed, checks=checks, errors=errors, warnings=warnings)
