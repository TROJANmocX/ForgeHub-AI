"""Tests for DataHub write-back payload generation."""
from __future__ import annotations

import pytest
from datetime import datetime

from app.datahub.writeback import (
    build_documentation_payload,
    build_lineage_payload,
    build_tag_payload,
)
from app.models.artifacts import GeneratedArtifact


@pytest.fixture
def sample_artifact():
    return GeneratedArtifact(
        run_id="test-run-001",
        dataset_id="orders",
        model_name="fct_orders",
        sql="SELECT order_id FROM retail.orders",
        schema_yml="version: 2\nmodels:\n  - name: fct_orders",
        readme="# fct_orders\nTest readme.",
        generated_at=datetime(2026, 1, 1, 12, 0, 0),
        llm_provider="mock",
    )


class TestWritebackPayloads:
    def test_lineage_payload_structure(self, sample_artifact):
        source_urn = "urn:li:dataset:(urn:li:dataPlatform:bigquery,retail.orders,PROD)"
        payload = build_lineage_payload(sample_artifact, source_urn)
        assert "entity" in payload
        assert "aspect" in payload
        aspect = payload["aspect"]
        assert "com.linkedin.dataset.UpstreamLineage" in aspect
        upstreams = aspect["com.linkedin.dataset.UpstreamLineage"]["upstreams"]
        assert len(upstreams) == 1
        assert upstreams[0]["dataset"] == source_urn

    def test_lineage_model_urn_format(self, sample_artifact):
        source_urn = "urn:li:dataset:(urn:li:dataPlatform:bigquery,retail.orders,PROD)"
        payload = build_lineage_payload(sample_artifact, source_urn)
        model_urn = payload["entity"]["com.linkedin.common.urn"]
        assert "fct_orders" in model_urn
        assert "dbt" in model_urn

    def test_documentation_payload(self, sample_artifact):
        dataset_urn = "urn:li:dataset:(urn:li:dataPlatform:dbt,forgehub.fct_orders,PROD)"
        payload = build_documentation_payload(sample_artifact, dataset_urn)
        assert "aspect" in payload
        aspect = payload["aspect"]
        assert "com.linkedin.common.InstitutionalMemory" in aspect
        elements = aspect["com.linkedin.common.InstitutionalMemory"]["elements"]
        assert len(elements) > 0
        assert "forgehub" in elements[0]["url"]

    def test_tag_payload(self, sample_artifact):
        dataset_urn = "urn:li:dataset:(urn:li:dataPlatform:dbt,forgehub.fct_orders,PROD)"
        payload = build_tag_payload(dataset_urn, ["ai-generated", "forgehub"])
        aspect = payload["aspect"]
        assert "com.linkedin.common.GlobalTags" in aspect
        tags = aspect["com.linkedin.common.GlobalTags"]["tags"]
        tag_urns = [t["tag"] for t in tags]
        assert any("ai-generated" in t for t in tag_urns)
        assert any("forgehub" in t for t in tag_urns)

    def test_lineage_type_is_transformed(self, sample_artifact):
        source_urn = "urn:li:dataset:(urn:li:dataPlatform:bigquery,retail.orders,PROD)"
        payload = build_lineage_payload(sample_artifact, source_urn)
        upstream = payload["aspect"]["com.linkedin.dataset.UpstreamLineage"]["upstreams"][0]
        assert upstream["type"] == "TRANSFORMED"
