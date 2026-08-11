"""ForgeHub AI — Dataset API routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.metadata_agent import MetadataAgent
from app.agents.quality_agent import MetadataGap, MetadataQualityReport, QualityAgent
from app.models.metadata import DatasetMetadata

router = APIRouter(prefix="/datasets", tags=["datasets"])

_metadata_agent = MetadataAgent()
_quality_agent = QualityAgent()


class GapResponse(BaseModel):
    type: str
    asset: str
    severity: str
    reason: str
    generation_impact: str


class DimensionScoreResponse(BaseModel):
    name: str
    score: float


class QualityReportResponse(BaseModel):
    dataset_name: str
    overall_score: float
    dimensions: list[DimensionScoreResponse]
    gaps: list[GapResponse]
    blocking_count: int
    warning_count: int
    informational_count: int


class DatasetSummary(BaseModel):
    id: str
    name: str
    platform: str
    environment: str
    description: str | None


class DatasetDetailResponse(BaseModel):
    id: str
    urn: str
    name: str
    platform: str
    environment: str
    description: str | None
    owners: list[str]
    domains: list[str]
    glossary_terms: list[str]
    tags: list[str]
    column_count: int
    upstream_count: int
    downstream_count: int
    quality: QualityReportResponse


def _to_quality_response(report: MetadataQualityReport) -> QualityReportResponse:
    return QualityReportResponse(
        dataset_name=report.dataset_name,
        overall_score=report.overall_score,
        dimensions=[
            DimensionScoreResponse(name=d.name, score=d.score)
            for d in report.dimensions
        ],
        gaps=[
            GapResponse(
                type=g.type,
                asset=g.asset,
                severity=g.severity,
                reason=g.reason,
                generation_impact=g.generation_impact,
            )
            for g in report.gaps
        ],
        blocking_count=len(report.blocking_gaps),
        warning_count=len(report.warning_gaps),
        informational_count=len(report.informational_gaps),
    )


@router.get("", response_model=list[DatasetSummary])
def list_datasets():
    """List all available datasets."""
    ids = _metadata_agent.list_datasets()
    result = []
    for did in ids:
        try:
            ds = _metadata_agent.fetch(did)
            result.append(
                DatasetSummary(
                    id=did,
                    name=ds.name,
                    platform=ds.platform,
                    environment=ds.environment,
                    description=ds.description,
                )
            )
        except ValueError:
            continue
    return result


@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
def get_dataset(dataset_id: str):
    """Get full metadata + quality report for a single dataset."""
    try:
        ds = _metadata_agent.fetch(dataset_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found")

    report = _quality_agent.score(ds)

    return DatasetDetailResponse(
        id=dataset_id,
        urn=ds.urn,
        name=ds.name,
        platform=ds.platform,
        environment=ds.environment,
        description=ds.description,
        owners=ds.owners,
        domains=ds.domains,
        glossary_terms=ds.glossary_terms,
        tags=ds.tags,
        column_count=len(ds.columns),
        upstream_count=len(ds.upstream_datasets),
        downstream_count=len(ds.downstream_datasets),
        quality=_to_quality_response(report),
    )
