"""
ForgeHub AI — DataHub Write-back
Constructs DataHub-compatible payloads for tags, documentation, lineage.
In DEMO_MODE these are logged only and not sent.
"""
from __future__ import annotations

import logging

from app.models.artifacts import GeneratedArtifact

logger = logging.getLogger(__name__)


def build_lineage_payload(artifact: GeneratedArtifact, source_urn: str) -> dict:
    """Build an upstream lineage aspect payload."""
    model_urn = f"urn:li:dataset:(urn:li:dataPlatform:dbt,forgehub.{artifact.model_name},PROD)"
    return {
        "entity": {
            "com.linkedin.common.urn": model_urn,
        },
        "aspect": {
            "com.linkedin.dataset.UpstreamLineage": {
                "upstreams": [
                    {
                        "dataset": source_urn,
                        "type": "TRANSFORMED",
                    }
                ]
            }
        },
    }


def build_documentation_payload(artifact: GeneratedArtifact, dataset_urn: str) -> dict:
    """Build an institutionalMemory (README) aspect payload."""
    return {
        "entity": {"com.linkedin.common.urn": dataset_urn},
        "aspect": {
            "com.linkedin.common.InstitutionalMemory": {
                "elements": [
                    {
                        "url": f"forgehub://artifacts/{artifact.run_id}",
                        "description": artifact.readme[:1000],
                        "createStamp": {
                            "actor": "urn:li:corpuser:forgehub-ai",
                            "time": int(artifact.generated_at.timestamp() * 1000),
                        },
                    }
                ]
            }
        },
    }


def build_tag_payload(dataset_urn: str, tags: list[str]) -> dict:
    """Build a globalTags aspect payload."""
    return {
        "entity": {"com.linkedin.common.urn": dataset_urn},
        "aspect": {
            "com.linkedin.common.GlobalTags": {
                "tags": [
                    {"tag": f"urn:li:tag:{tag}"} for tag in tags
                ]
            }
        },
    }


def log_writeback(payloads: list[dict]) -> None:
    """Log write-back payloads (used in demo mode)."""
    for p in payloads:
        logger.info("[DEMO WRITEBACK] %s", p)
