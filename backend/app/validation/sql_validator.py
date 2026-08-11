"""
ForgeHub AI — SQL AST Validator (powered by sqlglot)
Validates generated SQL against the verified symbol table.
Rejects hallucinated tables and columns mechanically.
"""
from __future__ import annotations

import sqlglot
import sqlglot.expressions as exp

from app.models.artifacts import ValidationCheck, ValidationReport


def _preprocess_dbt_jinja(sql: str) -> str:
    """Preprocess dbt Jinja macros like {{ source('schema', 'table') }} into standard SQL for sqlglot."""
    import re
    # {{ source('schema', 'table') }} -> schema.table
    cleaned = re.sub(
        r"\{\{\s*source\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)\s*\}\}",
        r"\1.\2",
        sql,
        flags=re.IGNORECASE,
    )
    # {{ ref('model') }} -> model
    cleaned = re.sub(
        r"\{\{\s*ref\s*\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\}\}",
        r"\1",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned


class SqlValidator:
    """
    Parses SQL into an AST and checks:
    1. Syntax validity
    2. Table references → symbol table
    3. Column references → symbol table
    4. Semantic function safety (deferred to SemanticValidator)
    """

    def validate(self, sql: str, symbol_table: dict[str, dict]) -> ValidationReport:
        checks: list[ValidationCheck] = []
        errors: list[str] = []
        warnings: list[str] = []

        # ── 1. Syntax check (preprocess Jinja macros first) ───────────────────
        clean_sql = _preprocess_dbt_jinja(sql)
        try:
            statements = sqlglot.parse(clean_sql, dialect="bigquery")
            if not statements or statements[0] is None:
                checks.append(ValidationCheck(name="SQL Syntax", passed=False, message="Empty or unparseable SQL"))
                errors.append("SQL_SYNTAX_ERROR: Could not parse SQL")
                return ValidationReport(passed=False, checks=checks, errors=errors, warnings=warnings)
            checks.append(ValidationCheck(name="SQL Syntax", passed=True))
        except sqlglot.errors.ParseError as exc:
            checks.append(ValidationCheck(name="SQL Syntax", passed=False, message=str(exc)))
            errors.append(f"SQL_SYNTAX_ERROR: {exc}")
            return ValidationReport(passed=False, checks=checks, errors=errors, warnings=warnings)

        # ─── Normalise symbol table keys to lowercase short names ─────────────
        # e.g. "retail.orders" → "orders" and "retail.orders" both accepted
        flat_tables: dict[str, set[str]] = {}
        for tbl_key, col_dict in symbol_table.items():
            short = tbl_key.split(".")[-1].lower()
            full = tbl_key.lower()
            flat_tables[short] = set(col_dict.keys())
            flat_tables[full] = set(col_dict.keys())

        # ── 2. Table reference check ──────────────────────────────────────────
        # Collect defined CTE names so we don't treat CTE references as unknown tables
        cte_names: set[str] = set()
        for cte in statements[0].find_all(exp.CTE):
            if cte.alias:
                cte_names.add(cte.alias.lower())

        table_errors: list[str] = []
        for node in statements[0].find_all(exp.Table):
            tbl_name = node.name.lower() if node.name else ""
            if not tbl_name or tbl_name in cte_names:
                continue
            db = node.args.get("db")
            full_ref = f"{db.name.lower()}.{tbl_name}" if db else tbl_name

            if full_ref not in flat_tables and tbl_name not in flat_tables:
                msg = f"UNKNOWN_TABLE: {full_ref}"
                table_errors.append(msg)

        if table_errors:
            for e in table_errors:
                errors.append(e)
            checks.append(ValidationCheck(name="Table References", passed=False, message="; ".join(table_errors)))
        else:
            checks.append(ValidationCheck(name="Table References", passed=True))

        # ── 3. Column reference check ─────────────────────────────────────────
        # Build set of ALL known columns across all verified tables
        all_known_columns: set[str] = set()
        for cols in flat_tables.values():
            all_known_columns.update(c.lower() for c in cols)

        # Also add derived/alias names from the SQL itself (CTEs, computed columns)
        # so we don't flag alias references as hallucinations
        alias_names: set[str] = set()
        for node in statements[0].find_all(exp.Alias):
            if node.alias:
                alias_names.add(node.alias.lower())

        column_errors: list[str] = []
        for node in statements[0].find_all(exp.Column):
            col_name = node.name.lower() if node.name else ""
            if not col_name or col_name in alias_names:
                continue
            # Skip star and built-in pseudo-columns
            if col_name in ("*", "true", "false", "null"):
                continue
            if col_name not in all_known_columns:
                msg = f"UNKNOWN_COLUMN: {col_name}"
                if msg not in column_errors:  # deduplicate
                    column_errors.append(msg)

        if column_errors:
            for e in column_errors:
                errors.append(e)
            checks.append(ValidationCheck(name="Column References", passed=False, message="; ".join(column_errors)))
        else:
            checks.append(ValidationCheck(name="Column References", passed=True))

        # ── 4. No SELECT * in base CTEs check ────────────────────────────────
        # Allow SELECT * only in the outermost final SELECT
        star_warnings: list[str] = []
        for node in statements[0].find_all(exp.Star):
            # Check if this star is inside a CTE
            parent = node.parent
            while parent:
                if isinstance(parent, exp.With):
                    star_warnings.append("SELECT * used inside a CTE — prefer explicit column list")
                    break
                parent = parent.parent

        if star_warnings:
            warnings.extend(star_warnings)
            checks.append(ValidationCheck(name="Explicit Columns", passed=False, message="; ".join(star_warnings)))
        else:
            checks.append(ValidationCheck(name="Explicit Columns", passed=True))

        passed = len(errors) == 0
        return ValidationReport(passed=passed, checks=checks, errors=errors, warnings=warnings)
