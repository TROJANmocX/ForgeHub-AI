"""ForgeHub AI — Publish API route."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.metadata_agent import MetadataAgent
from app.config import get_settings
from app.datahub.client import DataHubClient
from app.datahub.writeback import (
    build_documentation_payload,
    build_lineage_payload,
    build_tag_payload,
    log_writeback,
)
from app.models.generation import GenerationStatus

router = APIRouter(prefix="/publish", tags=["publish"])

_metadata_agent = MetadataAgent()
_datahub_client = DataHubClient()

# Reference to the in-memory run store (shared with generation.py via import)
from app.api.generation import _runs  # noqa: E402


from pydantic import BaseModel, ConfigDict


class PublishRequest(BaseModel):
    run_id: str
    approved: bool = True


class PublishResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    success: bool
    run_id: str
    status: str
    model_urn: str
    lineage: dict
    message: str



@router.post("", response_model=PublishResponse)
def publish(request: PublishRequest):
    """Publish a validated and approved artifact to DataHub."""
    run = _runs.get(request.run_id)
    if not run:
        raise HTTPException(status_code=404, detail=f"Run '{request.run_id}' not found")

    if not request.approved:
        raise HTTPException(status_code=400, detail="Artifact must be explicitly approved before publishing")

    artifact = run["artifact"]
    settings = get_settings()

    # Build the model URN
    model_urn = f"urn:li:dataset:(urn:li:dataPlatform:dbt,forgehub.{artifact.model_name},PROD)"

    # Build write-back payloads
    try:
        dataset = _metadata_agent.fetch(artifact.dataset_id)
        source_urn = dataset.urn
    except ValueError:
        source_urn = f"urn:li:dataset:(urn:li:dataPlatform:unknown,{artifact.dataset_id},PROD)"

    payloads = [
        build_lineage_payload(artifact, source_urn),
        build_documentation_payload(artifact, model_urn),
        build_tag_payload(model_urn, ["ai-generated", "forgehub"]),
    ]

    if settings.demo_mode:
        log_writeback(payloads)
        success = True
    else:
        success = _datahub_client.publish({"batch": payloads})

    # Update run status
    run["status"] = GenerationStatus.PUBLISHED if success else GenerationStatus.FAILED

    return PublishResponse(
        success=success,
        run_id=request.run_id,
        status=GenerationStatus.PUBLISHED.value if success else GenerationStatus.FAILED.value,
        model_urn=model_urn,
        lineage={
            "source": source_urn,
            "generated_model": model_urn,
            "type": "TRANSFORMED",
        },
        message=(
            f"Published successfully. Model '{artifact.model_name}' is now discoverable in DataHub."
            if success
            else "Publish failed. Check DataHub connectivity."
        ),
    )
