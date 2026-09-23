from datetime import datetime

from pydantic import BaseModel


class FactorOut(BaseModel):
    key: str
    label: str
    detail: str
    met: bool
    warning: bool
    score: float


class EvidenceItemOut(BaseModel):
    id: str
    index: int
    created_at: datetime
    source_name: str
    source_role: str
    description: str
    source_reliability: float
    location_name: str
    status: str
    incident_type: str
    conflicting: bool


class ScoreOut(BaseModel):
    source_reliability: float
    corroboration: float
    recency: float
    location_agreement: float
    evidence_quality: float
    contradiction_penalty: float
    confidence: float


class AssessmentOut(BaseModel):
    route_id: str
    route_name: str
    origin: str
    destination: str
    estimated_minutes: int
    distance_km: float
    state: str
    headline: str
    reason: str
    confidence: float
    last_updated: datetime | None
    updated_label: str | None
    freshness_label: str
    recent_reports: int
    independent_sources: int
    official_confirmation: bool
    cluster_location: str | None
    alternate_route_id: str | None
    scores: ScoreOut | None = None


class EvidenceOut(AssessmentOut):
    factors: list[FactorOut]
    reports: list[EvidenceItemOut]
    conflicting: list[EvidenceItemOut]
    disclaimer: str = "Strength of the reports we have. Not a safety guarantee."
