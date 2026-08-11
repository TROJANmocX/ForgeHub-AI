"""ForgeHub AI — DataHub metadata parsing utilities."""
from __future__ import annotations

from app.models.metadata import DatasetMetadata


def build_symbol_table(dataset: DatasetMetadata) -> dict[str, dict]:
    """
    Build a verified symbol table from DataHub metadata.
    Structure: { table_name: { column_name: ColumnMetadata } }
    The generation agent must ONLY reference symbols contained here.
    """
    return {
        dataset.name: {
            col.name: {
                "data_type": col.data_type,
                "semantic_type": col.semantic_type,
                "is_primary_key": col.is_primary_key,
                "is_foreign_key": col.is_foreign_key,
                "pii": col.pii,
            }
            for col in dataset.columns
        }
    }
