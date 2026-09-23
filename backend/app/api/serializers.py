from __future__ import annotations

import json

from app.models import Report, Route
from app.schemas.assessment import AssessmentOut, EvidenceItemOut, EvidenceOut, FactorOut, ScoreOut
from app.schemas.report import ReportOut
from app.schemas.route import RouteOut, RoutePoint
from app.services.assessment import human_updated_label
from app.services.types import AssessmentResult


def route_to_out(route: Route, result: AssessmentResult | None = None) -> RouteOut:
    geometry = json.loads(route.geometry)
    return RouteOut(
        id=route.id,
        name=route.name,
        origin=route.origin,
        destination=route.destination,
        estimated_minutes=route.estimated_minutes,
        distance_km=route.distance_km,
        alternate_of=route.alternate_of,
        geometry=geometry,
        segments=[
            RoutePoint(
                name=segment.name,
                latitude=segment.latitude,
                longitude=segment.longitude,
                sequence=segment.sequence,
            )
            for segment in sorted(route.segments, key=lambda item: item.sequence)
        ],
        state=result.state if result else None,
        confidence=result.confidence if result else None,
    )


def assessment_to_out(route: Route, result: AssessmentResult, alternate_id: str | None) -> AssessmentOut:
    scores = None
    if result.scores:
        scores = ScoreOut(
            source_reliability=result.scores.source_reliability,
            corroboration=result.scores.corroboration,
            recency=result.scores.recency,
            location_agreement=result.scores.location_agreement,
            evidence_quality=result.scores.evidence_quality,
            contradiction_penalty=result.scores.contradiction_penalty,
            confidence=result.scores.confidence,
        )
    return AssessmentOut(
        route_id=route.id,
        route_name=route.name,
        origin=route.origin,
        destination=route.destination,
        estimated_minutes=route.estimated_minutes,
        distance_km=route.distance_km,
        state=result.state,
        headline=result.headline,
        reason=result.reason,
        confidence=result.confidence,
        last_updated=result.last_updated,
        updated_label=human_updated_label(result.last_updated),
        freshness_label=result.freshness_label,
        recent_reports=result.recent_reports,
        independent_sources=result.independent_sources,
        official_confirmation=result.official_confirmation,
        cluster_location=result.cluster_location,
        alternate_route_id=alternate_id,
        scores=scores,
    )


def evidence_to_out(route: Route, result: AssessmentResult, alternate_id: str | None) -> EvidenceOut:
    base = assessment_to_out(route, result, alternate_id)
    return EvidenceOut(
        **base.model_dump(),
        factors=[FactorOut(**factor.__dict__) for factor in result.factors],
        reports=[EvidenceItemOut(**item.__dict__) for item in result.reports],
        conflicting=[EvidenceItemOut(**item.__dict__) for item in result.conflicting],
    )


def report_to_out(report: Report) -> ReportOut:
    user = report.user
    return ReportOut(
        id=report.id,
        user_id=report.user_id,
        user_name=user.name if user else "Unknown",
        user_role=user.role if user else "Unknown",
        incident_type=report.incident_type,
        description=report.description,
        latitude=report.latitude,
        longitude=report.longitude,
        location_name=report.location_name,
        created_at=report.created_at,
        status=report.status,
        severity=report.severity,
        source_reliability=user.reliability_score if user else 0.4,
        evidence_quality=report.evidence_quality,
        is_official=report.is_official,
    )
