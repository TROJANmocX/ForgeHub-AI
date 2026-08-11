"""
ForgeHub AI — Metadata Agent
Fetches, normalizes, and exposes dataset metadata + symbol table.
"""
from __future__ import annotations

from typing import Optional

from app.datahub.client import DataHubClient
from app.datahub.metadata import build_symbol_table
from app.models.metadata import DatasetMetadata


class MetadataAgent:
    """
    Responsible for retrieving verified DataHub metadata and constructing
    the symbol table that constrains all subsequent generation.
    """

    def __init__(self, client: Optional[DataHubClient] = None) -> None:
        self._client = client or DataHubClient()

    def list_datasets(self) -> list[str]:
        return self._client.list_datasets()

    def fetch(self, dataset_id: str) -> DatasetMetadata:
        """
        Fetch and return strongly-typed metadata.
        Raises ValueError if the dataset is not found.
        """
        dataset = self._client.get_dataset(dataset_id)
        if dataset is None:
            raise ValueError(f"Dataset not found: {dataset_id!r}")
        return dataset

    def get_symbol_table(self, dataset: DatasetMetadata) -> dict[str, dict]:
        """
        Return the verified symbol table. The generation agent must only
        reference tables and columns that appear here.
        """
        return build_symbol_table(dataset)
