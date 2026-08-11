"""Tests for SqlValidator — correct SQL passes, hallucinations are rejected."""
from __future__ import annotations

import pytest

from app.agents.metadata_agent import MetadataAgent
from app.validation.sql_validator import SqlValidator

ORDERS_SYMBOL_TABLE = {
    "retail.orders": {
        "order_id": {"data_type": "STRING", "semantic_type": "identifier"},
        "customer_id": {"data_type": "STRING", "semantic_type": "identifier"},
        "order_date": {"data_type": "DATE", "semantic_type": "date"},
        "quantity": {"data_type": "INTEGER", "semantic_type": "quantity"},
        "unit_price": {"data_type": "NUMERIC", "semantic_type": None},
        "status": {"data_type": "STRING", "semantic_type": "category"},
    }
}

_VALID_SQL = """
WITH orders AS (
    SELECT order_id, customer_id, quantity, unit_price
    FROM retail.orders
),
final AS (
    SELECT order_id, customer_id, quantity, unit_price,
           quantity * unit_price AS order_value
    FROM orders
)
SELECT * FROM final
"""

_HALLUCINATED_COL_SQL = """
SELECT customer_name, fake_revenue
FROM retail.orders
"""

_HALLUCINATED_TABLE_SQL = """
SELECT order_id
FROM retail.magic_orders
"""

_INVALID_SYNTAX_SQL = "SELECT * FORM retail.orders WHERE"


@pytest.fixture
def validator():
    return SqlValidator()


class TestSqlValidator:
    def test_valid_sql_passes(self, validator):
        report = validator.validate(sql=_VALID_SQL, symbol_table=ORDERS_SYMBOL_TABLE)
        assert report.passed is True
        assert len(report.errors) == 0

    def test_hallucinated_column_rejected(self, validator):
        report = validator.validate(sql=_HALLUCINATED_COL_SQL, symbol_table=ORDERS_SYMBOL_TABLE)
        assert report.passed is False
        error_text = " ".join(report.errors)
        assert "UNKNOWN_COLUMN" in error_text
        assert "customer_name" in error_text

    def test_hallucinated_table_rejected(self, validator):
        report = validator.validate(sql=_HALLUCINATED_TABLE_SQL, symbol_table=ORDERS_SYMBOL_TABLE)
        assert report.passed is False
        error_text = " ".join(report.errors)
        assert "UNKNOWN_TABLE" in error_text

    def test_invalid_syntax_rejected(self, validator):
        report = validator.validate(sql=_INVALID_SYNTAX_SQL, symbol_table=ORDERS_SYMBOL_TABLE)
        assert report.passed is False
        assert any("SYNTAX" in e.upper() for e in report.errors)

    def test_multiple_hallucinated_columns(self, validator):
        sql = "SELECT customer_name, fake_revenue, invented_metric FROM retail.orders"
        report = validator.validate(sql=sql, symbol_table=ORDERS_SYMBOL_TABLE)
        assert report.passed is False
        # Should flag all three hallucinated columns
        error_text = " ".join(report.errors)
        assert "customer_name" in error_text
        assert "fake_revenue" in error_text

    def test_syntax_check_comes_first(self, validator):
        """If syntax fails, table/column checks should not be reached."""
        report = validator.validate(sql="GARBAGE SQL @@##", symbol_table=ORDERS_SYMBOL_TABLE)
        assert report.passed is False
        assert any(c.name == "SQL Syntax" for c in report.checks)

    def test_validation_checks_named_correctly(self, validator):
        report = validator.validate(sql=_VALID_SQL, symbol_table=ORDERS_SYMBOL_TABLE)
        check_names = {c.name for c in report.checks}
        assert "SQL Syntax" in check_names
        assert "Table References" in check_names
        assert "Column References" in check_names
