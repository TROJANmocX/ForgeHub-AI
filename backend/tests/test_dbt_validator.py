"""Tests for DbtValidator — valid schema passes, hallucinated columns rejected."""
from __future__ import annotations

import pytest

from app.validation.dbt_validator import DbtValidator

SYMBOL_TABLE = {
    "retail.orders": {
        "order_id": {},
        "customer_id": {},
        "quantity": {},
        "unit_price": {},
        "status": {},
        "order_date": {},
    }
}

_VALID_SCHEMA = """
version: 2

models:
  - name: fct_orders
    description: "Fact table for orders."
    columns:
      - name: order_id
        description: "Unique order identifier."
        tests:
          - unique
          - not_null
      - name: customer_id
        description: "Customer FK."
        tests:
          - not_null
      - name: order_value
        description: "Derived: quantity * unit_price."
"""

_HALLUCINATED_SCHEMA = """
version: 2

models:
  - name: fct_orders
    columns:
      - name: customer_name
        description: "Hallucinated column."
      - name: fake_revenue
        description: "Hallucinated revenue."
"""

_NO_MODEL_SCHEMA = """
version: 2

sources:
  - name: retail
    tables:
      - name: orders
"""

_INVALID_YAML = "this: is: not: valid: yaml: ["

_MISSING_DESC_SCHEMA = """
version: 2

models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
"""


@pytest.fixture
def validator():
    return DbtValidator()


class TestDbtValidator:
    def test_valid_schema_passes(self, validator):
        report = validator.validate(
            schema_yml=_VALID_SCHEMA,
            symbol_table=SYMBOL_TABLE,
            model_name="fct_orders",
        )
        assert report.passed is True
        assert len(report.errors) == 0

    def test_hallucinated_columns_rejected(self, validator):
        report = validator.validate(
            schema_yml=_HALLUCINATED_SCHEMA,
            symbol_table=SYMBOL_TABLE,
            model_name="fct_orders",
        )
        assert report.passed is False
        error_text = " ".join(report.errors)
        assert "customer_name" in error_text or "HALLUCINATED" in error_text

    def test_no_models_section_rejected(self, validator):
        report = validator.validate(
            schema_yml=_NO_MODEL_SCHEMA,
            symbol_table=SYMBOL_TABLE,
            model_name="fct_orders",
        )
        assert report.passed is False
        assert any("no model" in e.lower() or "DBT_NO_MODEL" in e for e in report.errors)

    def test_invalid_yaml_rejected(self, validator):
        report = validator.validate(
            schema_yml=_INVALID_YAML,
            symbol_table=SYMBOL_TABLE,
            model_name="fct_orders",
        )
        assert report.passed is False
        assert any("PARSE" in e.upper() for e in report.errors)

    def test_missing_descriptions_produce_warning(self, validator):
        report = validator.validate(
            schema_yml=_MISSING_DESC_SCHEMA,
            symbol_table=SYMBOL_TABLE,
            model_name="fct_orders",
        )
        assert any("MISSING_DESCRIPTIONS" in w for w in report.warnings)

    def test_checks_are_named(self, validator):
        report = validator.validate(
            schema_yml=_VALID_SCHEMA,
            symbol_table=SYMBOL_TABLE,
            model_name="fct_orders",
        )
        check_names = {c.name for c in report.checks}
        assert "dbt YAML Parse" in check_names
        assert "dbt Model Present" in check_names
