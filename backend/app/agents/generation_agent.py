"""
ForgeHub AI — Generation Agent
Builds a structured prompt from the reasoning plan + symbol table,
calls the LLM provider, and manages the self-repair loop.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Optional

from app.config import get_settings
from app.llm.base import LLMProvider
from app.models.artifacts import GeneratedArtifact, ProvenanceDecision, ValidationCheck, ValidationReport
from app.models.metadata import DatasetMetadata
from app.models.reasoning import ReasoningPlan
from app.validation.dbt_validator import DbtValidator
from app.validation.sql_validator import SqlValidator

logger = logging.getLogger(__name__)


def _build_prompt(
    dataset: DatasetMetadata,
    plan: ReasoningPlan,
    symbol_table: dict,
    errors: list[str] | None = None,
) -> str:
    """Construct a tightly-constrained generation prompt."""
    symbol_json = json.dumps(symbol_table, indent=2)
    plan_json = plan.model_dump_json(indent=2)
    error_section = ""
    if errors:
        error_section = (
            "\n\n## REPAIR REQUIRED\n"
            "The previous generation failed validation with these errors:\n"
            + "\n".join(f"- {e}" for e in errors)
            + "\n\nFix ONLY the listed errors. Do not invent new columns or tables."
        )

    return f"""You are ForgeHub AI, a metadata-governed dbt model generator.

## STRICT RULES
1. You may ONLY reference tables and columns that appear in the Symbol Table below.
2. Any column or table NOT in the Symbol Table is FORBIDDEN.
3. Use dbt-compatible SQL with CTEs.
4. No SELECT * in intermediate CTEs.
5. Generate only what the metadata can support.

## Symbol Table (source of truth)
```json
{symbol_json}
```

## Reasoning Plan
```json
{plan_json}
```
{error_section}

## Output Format
Respond with ONLY a valid JSON object:
{{
  "sql": "<full dbt SQL>",
  "schema_yml": "<full schema.yml content>",
  "readme": "<full README.md content>"
}}
"""


class GenerationAgent:
    """
    Orchestrates: prompt → LLM → validate → repair loop → artifact.
    Enforces the symbol table contract mechanically, not by trusting the LLM.
    """

    def __init__(self, llm: LLMProvider, sql_validator: Optional[SqlValidator] = None) -> None:
        self._llm = llm
        self._sql_validator = sql_validator or SqlValidator()
        self._dbt_validator = DbtValidator()
        self._max_attempts = get_settings().max_repair_attempts

    def generate(
        self,
        dataset: DatasetMetadata,
        plan: ReasoningPlan,
        symbol_table: dict,
    ) -> GeneratedArtifact:
        import uuid

        run_id = str(uuid.uuid4())
        errors: list[str] = []
        repair_attempts = 0
        final_artifact: Optional[dict] = None
        last_validation: Optional[ValidationReport] = None

        for attempt in range(self._max_attempts + 1):
            # ── Call LLM ──────────────────────────────────────────────────────
            prompt = _build_prompt(dataset, plan, symbol_table, errors if attempt > 0 else None)
            raw = self._llm.generate(prompt)

            # ── Parse JSON response ───────────────────────────────────────────
            artifact_dict = self._parse_response(raw)
            if artifact_dict is None:
                errors = [f"LLM response was not valid JSON on attempt {attempt + 1}"]
                repair_attempts += 1
                continue

            # ── SQL validation ────────────────────────────────────────────────
            sql_report = self._sql_validator.validate(
                sql=artifact_dict.get("sql", ""),
                symbol_table=symbol_table,
            )

            # ── dbt YAML validation ───────────────────────────────────────────
            dbt_report = self._dbt_validator.validate(
                schema_yml=artifact_dict.get("schema_yml", ""),
                symbol_table=symbol_table,
                model_name=plan.model_name,
            )

            # ── Combined validation ───────────────────────────────────────────
            all_checks = sql_report.checks + dbt_report.checks
            all_errors = sql_report.errors + dbt_report.errors
            all_warnings = sql_report.warnings + dbt_report.warnings
            passed = sql_report.passed and dbt_report.passed

            last_validation = ValidationReport(
                passed=passed,
                checks=all_checks,
                errors=all_errors,
                warnings=all_warnings,
            )

            if passed:
                final_artifact = artifact_dict
                break

            # ── Repair loop ───────────────────────────────────────────────────
            errors = all_errors
            repair_attempts += 1
            logger.warning(
                "Generation attempt %d failed: %s", attempt + 1, errors
            )

        # ── Build provenance ──────────────────────────────────────────────────
        provenance = [
            ProvenanceDecision(
                decision=t.name,
                expression=t.expression,
                evidence=[e.model_dump() for e in t.evidence],
                confidence=t.confidence,
            )
            for t in plan.transformations
        ]

        if final_artifact is None:
            # All attempts failed — construct explicit failure report
            fail_errors = errors or [
                "Model generation failed: LLM output could not be parsed into valid JSON or validated after max repair attempts."
            ]
            if last_validation is None:
                last_validation = ValidationReport(
                    passed=False,
                    checks=[
                        ValidationCheck(
                            name="LLM Response Validation",
                            passed=False,
                            message="; ".join(fail_errors),
                        )
                    ],
                    errors=fail_errors,
                    warnings=[],
                )
            else:
                last_validation.passed = False
                if fail_errors and not last_validation.errors:
                    last_validation.errors = fail_errors

            return GeneratedArtifact(
                run_id=run_id,
                dataset_id=dataset.name,
                model_name=plan.model_name,
                sql="",
                schema_yml="",
                readme="",
                provenance=provenance,
                validation_report=last_validation,
                llm_provider=self._llm.name,
                repair_attempts=repair_attempts,
            )

        return GeneratedArtifact(
            run_id=run_id,
            dataset_id=dataset.name,
            model_name=plan.model_name,
            sql=final_artifact.get("sql", ""),
            schema_yml=final_artifact.get("schema_yml", ""),
            readme=final_artifact.get("readme", ""),
            provenance=provenance,
            validation_report=last_validation,
            llm_provider=self._llm.name,
            repair_attempts=repair_attempts,
        )

    def _parse_response(self, raw: str) -> Optional[dict]:
        """Extract JSON from LLM response, tolerating markdown code fences and conversational preamble."""
        text = raw.strip()
        if not text:
            return None

        # 1. Try direct JSON parse
        try:
            val = json.loads(text)
            if isinstance(val, dict) and "sql" in val:
                return val
        except json.JSONDecodeError:
            pass

        # 2. Try extracting from markdown ```json ... ``` or ``` ... ``` block
        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fence_match:
            try:
                val = json.loads(fence_match.group(1))
                if isinstance(val, dict):
                    return val
            except json.JSONDecodeError:
                pass

        # 3. Fallback: find outermost '{' and '}'
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                val = json.loads(text[start : end + 1])
                if isinstance(val, dict):
                    return val
            except json.JSONDecodeError:
                pass

        return None

