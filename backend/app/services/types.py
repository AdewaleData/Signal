from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

INCIDENT_TYPES = (
    "road_blocked",
    "crowd_gathering",
    "accident",
    "fire",
    "security_incident",
    "other",
    "all_clear",
)

HAZARD_TYPES = {
    "road_blocked",
    "crowd_gathering",
    "accident",
    "fire",
    "security_incident",
    "other",
}

CLEAR_TYPES = {"all_clear"}

INCIDENT_LABELS = {
    "road_blocked": "Road blocked",
    "crowd_gathering": "Crowd / gathering",
    "accident": "Accident",
    "fire": "Fire",
    "security_incident": "Security incident",
    "other": "Other",
    "all_clear": "Road appears clear",
}

STATE_CLEAR = "CLEAR"
STATE_CAUTION = "CAUTION"
STATE_AVOID = "AVOID"
STATE_UNKNOWN = "UNKNOWN"

REL_CORROBORATES = "CORROBORATES"
REL_CONTRADICTS = "CONTRADICTS"
REL_UNRELATED = "UNRELATED"


@dataclass
class SignalInput:
    id: str
    user_id: str
    user_name: str
    user_role: str
    reliability_score: float
    incident_type: str
    description: str
    latitude: float
    longitude: float
    location_name: str
    created_at: datetime
    status: str = "active"
    severity: str = "medium"
    evidence_quality: float = 0.45
    is_official: bool = False


@dataclass
class RelationshipResult:
    report_id: str
    related_report_id: str
    relationship_type: str
    similarity_score: float


@dataclass
class FactorResult:
    key: str
    label: str
    detail: str
    met: bool
    warning: bool = False
    score: float = 0.0


@dataclass
class EvidenceReport:
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
    conflicting: bool = False


@dataclass
class ScoreBreakdown:
    source_reliability: float
    corroboration: float
    recency: float
    location_agreement: float
    evidence_quality: float
    contradiction_penalty: float
    raw_confidence: float
    confidence: float


@dataclass
class AssessmentResult:
    state: str
    confidence: float
    headline: str
    reason: str
    last_updated: datetime | None
    recent_reports: int
    independent_sources: int
    official_confirmation: bool
    freshness_label: str
    factors: list[FactorResult] = field(default_factory=list)
    reports: list[EvidenceReport] = field(default_factory=list)
    conflicting: list[EvidenceReport] = field(default_factory=list)
    scores: ScoreBreakdown | None = None
    relationships: list[RelationshipResult] = field(default_factory=list)
    cluster_location: str | None = None
