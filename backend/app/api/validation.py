"""ForgeHub AI — Standalone validation API route."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from app.agents.metadata_agent import MetadataAgent
from app.validation.dbt_validator import DbtValidator
from app.validation.sql_validator import SqlValidator

router = APIRouter(prefix="/validate", tags=["validation"])

_metadata_agent = MetadataAgent()
_sql_validator = SqlValidator()
_dbt_validator = DbtValidator()


class ValidateRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    dataset_id: str
    sql: str
    schema_yml: str = ""
    model_name: str = "model"


class ValidateResponse(BaseModel):
    passed: bool
    checks: list[dict]
    errors: list[str]
    warnings: list[str]


@router.post("", response_model=ValidateResponse)
def validate(request: ValidateRequest):
    """Validate SQL and dbt schema against the dataset symbol table."""
    try:
        dataset = _metadata_agent.fetch(request.dataset_id)
    except ValueError:
        return ValidateResponse(
            passed=False,
            checks=[],
            errors=[f"Dataset '{request.dataset_id}' not found"],
            warnings=[],
        )

    symbol_table = _metadata_agent.get_symbol_table(dataset)

    sql_report = _sql_validator.validate(sql=request.sql, symbol_table=symbol_table)

    all_checks = [c.model_dump() for c in sql_report.checks]
    all_errors = list(sql_report.errors)
    all_warnings = list(sql_report.warnings)
    passed = sql_report.passed

    if request.schema_yml:
        dbt_report = _dbt_validator.validate(
            schema_yml=request.schema_yml,
            symbol_table=symbol_table,
            model_name=request.model_name,
        )
        all_checks += [c.model_dump() for c in dbt_report.checks]
        all_errors += dbt_report.errors
        all_warnings += dbt_report.warnings
        passed = passed and dbt_report.passed

    return ValidateResponse(
        passed=passed,
        checks=all_checks,
        errors=all_errors,
        warnings=all_warnings,
    )
