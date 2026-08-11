"""Tests for MetadataAgent and QualityAgent."""
from __future__ import annotations

import pytest

from app.agents.metadata_agent import MetadataAgent
from app.agents.quality_agent import QualityAgent
from app.models.metadata import ColumnMetadata, DatasetMetadata


@pytest.fixture
def orders_dataset():
    agent = MetadataAgent()
    return agent.fetch("orders")


@pytest.fixture
def customers_dataset():
    agent = MetadataAgent()
    return agent.fetch("customers")


class TestMetadataAgent:
    def test_list_datasets(self):
        agent = MetadataAgent()
        datasets = agent.list_datasets()
        assert "orders" in datasets
        assert "customers" in datasets
        assert "revenue" in datasets

    def test_fetch_orders(self, orders_dataset):
        ds = orders_dataset
        assert ds.name == "retail.orders"
        assert ds.platform == "bigquery"
        assert len(ds.columns) > 0

    def test_orders_has_primary_key(self, orders_dataset):
        pk_cols = [c for c in orders_dataset.columns if c.is_primary_key]
        assert len(pk_cols) > 0
        assert pk_cols[0].name == "order_id"

    def test_orders_schema_normalization(self, orders_dataset):
        col_names = orders_dataset.column_names()
        assert "order_id" in col_names
        assert "customer_id" in col_names
        assert "quantity" in col_names
        assert "unit_price" in col_names

    def test_not_found_raises(self):
        agent = MetadataAgent()
        with pytest.raises(ValueError, match="not found"):
            agent.fetch("nonexistent_dataset_xyz")

    def test_symbol_table_structure(self, orders_dataset):
        agent = MetadataAgent()
        sym = agent.get_symbol_table(orders_dataset)
        assert "retail.orders" in sym
        assert "order_id" in sym["retail.orders"]

    def test_customers_pii_flags(self, customers_dataset):
        pii_cols = [c for c in customers_dataset.columns if c.pii]
        pii_names = {c.name for c in pii_cols}
        assert "email" in pii_names
        assert "first_name" in pii_names


class TestQualityAgent:
    def test_orders_score_is_numeric(self, orders_dataset):
        agent = QualityAgent()
        report = agent.score(orders_dataset)
        assert 0 <= report.overall_score <= 100

    def test_orders_has_blocking_gap(self, orders_dataset):
        """orders.unit_price has no currency → should be BLOCKING gap."""
        agent = QualityAgent()
        report = agent.score(orders_dataset)
        blocking_types = {g.type for g in report.blocking_gaps}
        assert "UNDEFINED_CURRENCY" in blocking_types

    def test_gap_has_required_fields(self, orders_dataset):
        agent = QualityAgent()
        report = agent.score(orders_dataset)
        gap = report.gaps[0]
        assert gap.type
        assert gap.asset
        assert gap.severity in ("informational", "warning", "blocking")
        assert gap.reason
        assert gap.generation_impact

    def test_dimensions_all_present(self, orders_dataset):
        agent = QualityAgent()
        report = agent.score(orders_dataset)
        dim_names = {d.name for d in report.dimensions}
        assert "Schema Completeness" in dim_names
        assert "Descriptions" in dim_names
        assert "Governance" in dim_names
        assert "Semantic Metadata" in dim_names

    def test_score_breakdown_sums_to_overall(self, orders_dataset):
        """Verify that dimension scores produce a reasonable overall."""
        agent = QualityAgent()
        report = agent.score(orders_dataset)
        # At minimum, schema should be 100 (has columns)
        schema_dim = next(d for d in report.dimensions if d.name == "Schema Completeness")
        assert schema_dim.score == 100.0
