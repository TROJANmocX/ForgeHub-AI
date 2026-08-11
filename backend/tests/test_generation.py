"""
ForgeHub AI — Unit tests for GenerationAgent and the /generate endpoint.
"""
from __future__ import annotations

import json
import pytest
from fastapi.testclient import TestClient

from app.agents.generation_agent import GenerationAgent
from app.llm.base import LLMProvider
from app.llm.mock import MockProvider
from app.main import app
from app.models.metadata import ColumnMetadata, DatasetMetadata

client = TestClient(app)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_dataset(dataset_id: str = "orders") -> DatasetMetadata:
    """Return a minimal DatasetMetadata for testing."""
    cols = [
        ColumnMetadata(name="order_id", data_type="INTEGER", is_primary_key=True, semantic_type="identifier"),
        ColumnMetadata(name="customer_id", data_type="INTEGER", is_foreign_key=True),
        ColumnMetadata(name="order_date", data_type="DATE"),
        ColumnMetadata(name="quantity", data_type="INTEGER", semantic_type="quantity"),
        ColumnMetadata(name="unit_price", data_type="FLOAT"),
        ColumnMetadata(name="status", data_type="VARCHAR"),
    ]
    return DatasetMetadata(
        urn=f"urn:li:dataset:(urn:li:dataPlatform:bigquery,retail.{dataset_id},PROD)",
        name=f"retail.{dataset_id}",
        platform="bigquery",
        environment="PROD",
        columns=cols,
    )


SYMBOL_TABLE = {
    "retail.orders": {
        "order_id": {"data_type": "INTEGER"},
        "customer_id": {"data_type": "INTEGER"},
        "order_date": {"data_type": "DATE"},
        "quantity": {"data_type": "INTEGER"},
        "unit_price": {"data_type": "FLOAT"},
        "status": {"data_type": "VARCHAR"},
    }
}


# ─── _parse_response tests ─────────────────────────────────────────────────────

class AlwaysProvider(LLMProvider):
    """Returns a fixed response string."""
    def __init__(self, response: str):
        self._response = response

    def generate(self, prompt: str) -> str:
        return self._response

    @property
    def name(self) -> str:
        return "always"


VALID_ARTIFACT = json.dumps({
    "sql": "SELECT order_id FROM {{ source('retail', 'orders') }}",
    "schema_yml": "version: 2\nmodels:\n  - name: fct_orders\n    columns:\n      - name: order_id\n        tests:\n          - unique\n          - not_null",
    "readme": "# fct_orders",
})


def make_agent(response: str) -> GenerationAgent:
    return GenerationAgent(llm=AlwaysProvider(response))


def test_parse_plain_json():
    agent = make_agent(VALID_ARTIFACT)
    result = agent._parse_response(VALID_ARTIFACT)
    assert result is not None
    assert "sql" in result


def test_parse_json_with_markdown_fence():
    wrapped = f"Here is your output:\n```json\n{VALID_ARTIFACT}\n```"
    agent = make_agent(wrapped)
    result = agent._parse_response(wrapped)
    assert result is not None
    assert "sql" in result


def test_parse_json_with_backtick_fence():
    wrapped = f"```\n{VALID_ARTIFACT}\n```"
    agent = make_agent(wrapped)
    result = agent._parse_response(wrapped)
    assert result is not None
    assert "sql" in result


def test_parse_json_with_preamble():
    wrapped = f"Sure! Here is the dbt model:\n\n{VALID_ARTIFACT}\n\nLet me know if you need changes."
    agent = make_agent(wrapped)
    result = agent._parse_response(wrapped)
    assert result is not None
    assert "sql" in result


def test_parse_empty_returns_none():
    agent = make_agent("")
    assert agent._parse_response("") is None


def test_parse_non_json_returns_none():
    agent = make_agent("This is not JSON at all.")
    assert agent._parse_response("This is not JSON at all.") is None


# ─── Full GenerationAgent loop tests ──────────────────────────────────────────

def _build_plan_for(dataset: DatasetMetadata):
    from app.agents.reasoning_agent import ReasoningAgent
    return ReasoningAgent().build_plan(dataset)


def test_generate_success_with_mock():
    """Mock provider returns valid pre-baked SQL — should produce VALIDATED artifact."""
    from app.agents.metadata_agent import MetadataAgent
    agent_meta = MetadataAgent()
    dataset = agent_meta.fetch("orders")
    symbol_table = agent_meta.get_symbol_table(dataset)

    from app.agents.reasoning_agent import ReasoningAgent
    plan = ReasoningAgent().build_plan(dataset)

    llm = MockProvider(dataset_id="orders", broken=False)
    gen = GenerationAgent(llm=llm)
    artifact = gen.generate(dataset=dataset, plan=plan, symbol_table=symbol_table)

    assert artifact.sql != "", "SQL must not be empty on success"
    assert artifact.validation_report is not None
    assert artifact.validation_report.passed is True, f"Expected passed, errors: {artifact.validation_report.errors}"
    assert artifact.repair_attempts == 0


def test_generate_broken_returns_failed():
    """Broken mock returns hallucinated columns — validation must fail."""
    from app.agents.metadata_agent import MetadataAgent
    agent_meta = MetadataAgent()
    dataset = agent_meta.fetch("orders")
    symbol_table = agent_meta.get_symbol_table(dataset)

    from app.agents.reasoning_agent import ReasoningAgent
    plan = ReasoningAgent().build_plan(dataset)

    llm = MockProvider(dataset_id="orders", broken=True)
    gen = GenerationAgent(llm=llm)
    artifact = gen.generate(dataset=dataset, plan=plan, symbol_table=symbol_table)

    assert artifact.validation_report is not None
    assert artifact.validation_report.passed is False
    assert len(artifact.validation_report.errors) > 0


def test_generate_all_attempts_failed_returns_explicit_failure():
    """If the LLM always returns invalid JSON, artifact must have explicit failure report."""
    from app.agents.metadata_agent import MetadataAgent
    agent_meta = MetadataAgent()
    dataset = agent_meta.fetch("orders")
    symbol_table = agent_meta.get_symbol_table(dataset)
    from app.agents.reasoning_agent import ReasoningAgent
    plan = ReasoningAgent().build_plan(dataset)

    llm = AlwaysProvider("not valid json at all")
    gen = GenerationAgent(llm=llm)
    artifact = gen.generate(dataset=dataset, plan=plan, symbol_table=symbol_table)

    assert artifact.sql == ""
    assert artifact.validation_report is not None
    assert artifact.validation_report.passed is False
    assert len(artifact.validation_report.errors) > 0


# ─── Endpoint integration tests ───────────────────────────────────────────────

@pytest.mark.parametrize("dataset_id,expected_status_ok", [
    ("orders", True),
    ("customers", True),
    ("revenue", True),
])
def test_generate_endpoint_returns_200(dataset_id, expected_status_ok):
    resp = client.post("/generate", json={"dataset_id": dataset_id, "broken_mode": False})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("VALIDATED", "REQUIRES_REVIEW", "FAILED")
    assert "sql" in data
    assert "validation" in data
    assert "repair_attempts" in data


def test_generate_endpoint_broken_mode_returns_failed():
    resp = client.post("/generate", json={"dataset_id": "orders", "broken_mode": True})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "FAILED"
    assert data["validation"]["passed"] is False
    assert len(data["validation"]["errors"]) > 0


def test_generate_endpoint_unknown_dataset_returns_404():
    resp = client.post("/generate", json={"dataset_id": "does_not_exist", "broken_mode": False})
    assert resp.status_code == 404


def test_generate_endpoint_empty_sql_is_not_validated():
    """Ensure that an empty SQL result is always marked FAILED, never VALIDATED."""
    resp = client.post("/generate", json={"dataset_id": "orders", "broken_mode": False})
    assert resp.status_code == 200
    data = resp.json()
    if not data["sql"].strip():
        assert data["status"] == "FAILED", "Empty SQL must not be VALIDATED"
