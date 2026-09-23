from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Report, ReportRelationship, Route, RouteAssessment, User
from app.services.assessment import assess_signals, parse_geometry
from app.services.corroboration import build_relationships
from app.services.freshness import utc_now
from app.services.types import AssessmentResult, SignalInput


def signals_from_db(db: Session) -> list[SignalInput]:
    reports = db.scalars(select(Report).options(joinedload(Report.user))).all()
    return [signal_from_report(report) for report in reports]


def signal_from_report(report: Report) -> SignalInput:
    user = report.user
    return SignalInput(
        id=report.id,
        user_id=report.user_id,
        user_name=user.name if user else "Unknown",
        user_role=user.role if user else "Unknown",
        reliability_score=user.reliability_score if user else 0.4,
        incident_type=report.incident_type,
        description=report.description,
        latitude=report.latitude,
        longitude=report.longitude,
        location_name=report.location_name,
        created_at=report.created_at,
        status=report.status,
        severity=report.severity,
        evidence_quality=report.evidence_quality,
        is_official=report.is_official,
    )


def persist_relationships(db: Session, signals: list[SignalInput]) -> None:
    existing = {(row.report_id, row.related_report_id) for row in db.scalars(select(ReportRelationship)).all()}
    for rel in build_relationships(signals):
        key = (rel.report_id, rel.related_report_id)
        if key in existing:
            continue
        db.add(
            ReportRelationship(
                id=f"rel-{uuid4().hex[:12]}",
                report_id=rel.report_id,
                related_report_id=rel.related_report_id,
                relationship_type=rel.relationship_type,
                similarity_score=rel.similarity_score,
            )
        )


def persist_assessment(db: Session, route_id: str, result: AssessmentResult) -> RouteAssessment:
    now = utc_now()
    row = RouteAssessment(
        id=f"assess-{uuid4().hex[:12]}",
        route_id=route_id,
        state=result.state,
        confidence=result.confidence,
        reason=result.reason,
        created_at=now,
        expires_at=now + timedelta(minutes=30),
    )
    db.add(row)
    return row


def recompute_all_routes(db: Session) -> dict[str, AssessmentResult]:
    signals = signals_from_db(db)
    persist_relationships(db, signals)
    results: dict[str, AssessmentResult] = {}
    for route in db.scalars(select(Route)).all():
        geometry = parse_geometry(route.geometry)
        result = assess_signals(signals, geometry=geometry, route_name=route.name)
        persist_assessment(db, route.id, result)
        results[route.id] = result
    db.commit()
    return results


def recompute_route(db: Session, route: Route) -> AssessmentResult:
    signals = signals_from_db(db)
    persist_relationships(db, signals)
    result = assess_signals(signals, geometry=parse_geometry(route.geometry), route_name=route.name)
    persist_assessment(db, route.id, result)
    db.commit()
    return result


def get_user(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)
