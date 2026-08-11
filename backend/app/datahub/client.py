"""
ForgeHub AI — DataHub Client
In DEMO_MODE: loads metadata from local JSON fixtures.
In production mode: calls the DataHub REST API.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import httpx

from app.config import get_settings
from app.models.metadata import ColumnMetadata, DatasetMetadata

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Map short fixture keys → fixture filenames
FIXTURE_REGISTRY: dict[str, str] = {
    "orders": "orders.json",
    "customers": "customers.json",
    "revenue": "revenue.json",
}


def _load_fixture(key: str) -> dict:
    path = FIXTURES_DIR / FIXTURE_REGISTRY[key]
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _parse_dataset(raw: dict) -> DatasetMetadata:
    columns = [
        ColumnMetadata(
            name=col["name"],
            data_type=col["data_type"],
            description=col.get("description"),
            glossary_terms=col.get("glossary_terms", []),
            tags=col.get("tags", []),
            nullable=col.get("nullable"),
            is_primary_key=col.get("is_primary_key", False),
            is_foreign_key=col.get("is_foreign_key", False),
            semantic_type=col.get("semantic_type"),
            pii=col.get("pii", False),
        )
        for col in raw.get("columns", [])
    ]
    return DatasetMetadata(
        urn=raw["urn"],
        name=raw["name"],
        platform=raw["platform"],
        environment=raw["environment"],
        description=raw.get("description"),
        columns=columns,
        owners=raw.get("owners", []),
        domains=raw.get("domains", []),
        glossary_terms=raw.get("glossary_terms", []),
        tags=raw.get("tags", []),
        upstream_datasets=raw.get("upstream_datasets", []),
        downstream_datasets=raw.get("downstream_datasets", []),
        custom_properties=raw.get("custom_properties", {}),
    )


class DataHubClient:
    """Unified DataHub client. Switches between demo fixtures and live API."""

    def __init__(self) -> None:
        self._settings = get_settings()

    # ─── Dataset listing ──────────────────────────────────────────────────────

    def list_datasets(self) -> list[str]:
        """Return available dataset IDs."""
        if self._settings.demo_mode:
            return list(FIXTURE_REGISTRY.keys())
        return self._live_list_datasets()

    # ─── Single dataset fetch ─────────────────────────────────────────────────

    def get_dataset(self, dataset_id: str) -> Optional[DatasetMetadata]:
        """Fetch and parse metadata for a single dataset."""
        if self._settings.demo_mode:
            if dataset_id not in FIXTURE_REGISTRY:
                return None
            raw = _load_fixture(dataset_id)
            return _parse_dataset(raw)
        return self._live_get_dataset(dataset_id)

    # ─── Write-back stub ──────────────────────────────────────────────────────

    def publish(self, payload: dict) -> bool:
        """Publish metadata back to DataHub (no-op in demo mode)."""
        if self._settings.demo_mode:
            return True
        return self._live_publish(payload)

    # ─── Live API helpers ─────────────────────────────────────────────────────

    def _live_list_datasets(self) -> list[str]:
        url = f"{self._settings.datahub_url}/openapi/v3/entity/dataset"
        headers = {"Authorization": f"Bearer {self._settings.datahub_token}"}
        with httpx.Client(timeout=10) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return [e["urn"] for e in data.get("entities", [])]

    def _live_get_dataset(self, dataset_id: str) -> Optional[DatasetMetadata]:
        url = f"{self._settings.datahub_url}/openapi/v3/entity/dataset/{dataset_id}"
        headers = {"Authorization": f"Bearer {self._settings.datahub_token}"}
        with httpx.Client(timeout=10) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return _parse_dataset(resp.json())

    def _live_publish(self, payload: dict) -> bool:
        url = f"{self._settings.datahub_url}/openapi/v3/entity"
        headers = {
            "Authorization": f"Bearer {self._settings.datahub_token}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=payload, headers=headers)
            return resp.is_success
