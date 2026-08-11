"""Tests for SemanticValidator — currency mixing, percentage SUM, identifier arithmetic."""
from __future__ import annotations

import pytest

from app.models.metadata import ColumnMetadata, DatasetMetadata
from app.validation.semantic_validator import SemanticValidator


def _make_dataset(columns: list[dict]) -> DatasetMetadata:
    return DatasetMetadata(
        urn="urn:li:dataset:(urn:li:dataPlatform:bigquery,test.table,PROD)",
        name="test.table",
        platform="bigquery",
        environment="PROD",
        columns=[ColumnMetadata(**c) for c in columns],
    )


@pytest.fixture
def validator():
    return SemanticValidator()


class TestSemanticValidator:
    def test_valid_query_passes(self, validator):
        dataset = _make_dataset([
            {"name": "order_id", "data_type": "STRING", "semantic_type": "identifier"},
            {"name": "quantity", "data_type": "INTEGER", "semantic_type": "quantity"},
        ])
        sql = "SELECT order_id, SUM(quantity) FROM test.table GROUP BY order_id"
        report = validator.validate(sql=sql, dataset=dataset)
        assert report.passed is True

    def test_mixed_currency_detected(self, validator):
        dataset = _make_dataset([
            {"name": "revenue_usd", "data_type": "NUMERIC", "semantic_type": "currency_usd"},
            {"name": "revenue_eur", "data_type": "NUMERIC", "semantic_type": "currency_eur"},
        ])
        sql = "SELECT SUM(revenue_usd + revenue_eur) FROM test.table"
        report = validator.validate(sql=sql, dataset=dataset)
        assert report.passed is False
        assert any("Mixed-currency" in e for e in report.errors)

    def test_percentage_sum_rejected(self, validator):
        dataset = _make_dataset([
            {"name": "discount_rate", "data_type": "NUMERIC", "semantic_type": "percentage"},
        ])
        sql = "SELECT SUM(discount_rate) FROM test.table"
        report = validator.validate(sql=sql, dataset=dataset)
        assert report.passed is False
        assert any("SUM(discount_rate)" in e for e in report.errors)

    def test_percentage_avg_allowed(self, validator):
        dataset = _make_dataset([
            {"name": "discount_rate", "data_type": "NUMERIC", "semantic_type": "percentage"},
        ])
        sql = "SELECT AVG(discount_rate) FROM test.table"
        report = validator.validate(sql=sql, dataset=dataset)
        # AVG on a percentage is valid — should pass or only warn
        assert "SUM(discount_rate)" not in " ".join(report.errors)

    def test_identifier_arithmetic_rejected(self, validator):
        dataset = _make_dataset([
            {"name": "order_id", "data_type": "STRING", "semantic_type": "identifier"},
        ])
        sql = "SELECT SUM(order_id) FROM test.table"
        report = validator.validate(sql=sql, dataset=dataset)
        assert report.passed is False
        assert any("identifier" in e.lower() for e in report.errors)

    def test_undefined_currency_produces_warning(self, validator):
        dataset = _make_dataset([
            {"name": "unit_price", "data_type": "NUMERIC", "semantic_type": None},
        ])
        sql = "SELECT unit_price FROM test.table"
        report = validator.validate(sql=sql, dataset=dataset)
        # Should warn (not block) about undefined currency
        assert any("UNDEFINED_CURRENCY" in w for w in report.warnings)

    def test_single_currency_no_mixing_error(self, validator):
        dataset = _make_dataset([
            {"name": "revenue_usd", "data_type": "NUMERIC", "semantic_type": "currency_usd"},
            {"name": "cost_usd", "data_type": "NUMERIC", "semantic_type": "currency_usd"},
        ])
        sql = "SELECT SUM(revenue_usd), SUM(cost_usd) FROM test.table"
        report = validator.validate(sql=sql, dataset=dataset)
        # Same currency — no mixing error
        assert not any("Mixed-currency" in e for e in report.errors)
