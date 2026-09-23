from __future__ import annotations

import json
from datetime import datetime

from app.core.config import Settings, settings
from app.core.locations import resolve_place, road_key_from_name
from app.services.confidence import compute_confidence, independent_source_ids
from app.services.corroboration import build_relationships, cluster_reports, location_related
from app.services.explanation import (
    HEADLINES,
    attach_copy,
    build_factors,
    minutes_label,
    reason_for,
)
from app.services.freshness import (
    FRESHNESS_LABELS,
    age_minutes,
    as_utc,
    freshness_band,
    is_expired,
    utc_now,
)
from app.services.geo import nearest_distance_to_path
from app.services.types import (
    CLEAR_TYPES,
    HAZARD_TYPES,
    REL_CONTRADICTS,
    STATE_AVOID,
    STATE_CAUTION,
    STATE_CLEAR,
    STATE_UNKNOWN,
    AssessmentResult,
    EvidenceReport,
    ScoreBreakdown,
    SignalInput,
)


def parse_geometry(raw: str) -> list[tuple[float, float]]:
    data = json.loads(raw)
    return [(float(point[0]), float(point[1])) for point in data]


def report_affects_route(
    report: SignalInput,
    geometry: list[tuple[float, float]],
    route_name: str,
    cfg: Settings | None = None,
) -> bool:
    cfg = cfg or settings
    route_key = route_name.lower().replace(" ", "-")
    named_road = road_key_from_name(report.location_name)
    place = resolve_place(report.location_name)

    if named_road:
        return named_road == route_key or bool(place and route_key in place.roads)

    if place:
        if route_key in place.roads:
            return True
        if place.roads and route_key not in place.roads:
            return False

    if route_name.lower() in report.location_name.lower():
        return True

    distance = nearest_distance_to_path(report.latitude, report.longitude, geometry)
    return distance <= cfg.route_proximity_meters


def active_reports(reports: list[SignalInput], now: datetime | None, cfg: Settings) -> list[SignalInput]:
    kept: list[SignalInput] = []
    for report in reports:
        if report.status in {"expired", "resolved"}:
            continue
        if is_expired(age_minutes(report.created_at, now), cfg):
            continue
        kept.append(report)
    return kept


def decide_state(
    hazard_reports: list[SignalInput],
    clear_reports: list[SignalInput],
    scores: ScoreBreakdown | None,
    cfg: Settings,
) -> str:
    """Deterministic state machine. Absence of reports is UNKNOWN, never CLEAR."""
    if not hazard_reports:
        if _enough_clear_evidence(clear_reports, cfg):
            return STATE_CLEAR
        return STATE_UNKNOWN

    assert scores is not None
    independent = independent_source_ids(hazard_reports)
    strong_location = scores.location_agreement >= cfg.strong_location_agreement
    incident_active = scores.recency > 0.0

    if (
        scores.confidence >= cfg.avoid_confidence_threshold
        and len(independent) >= cfg.avoid_min_independent_sources
        and strong_location
        and incident_active
        and scores.contradiction_penalty < 0.18
    ):
        return STATE_AVOID

    return STATE_CAUTION


def _enough_clear_evidence(clear_reports: list[SignalInput], cfg: Settings) -> bool:
    if not clear_reports:
        return False
    official = [report for report in clear_reports if report.is_official]
    independent = independent_source_ids(clear_reports)
    if official:
        return True
    return len(independent) >= cfg.avoid_min_independent_sources


def _to_evidence(reports: list[SignalInput], conflicting: bool = False) -> list[EvidenceReport]:
    ordered = sorted(reports, key=lambda item: as_utc(item.created_at))
    items: list[EvidenceReport] = []
    for index, report in enumerate(ordered, start=1):
        items.append(
            EvidenceReport(
                id=report.id,
                index=index,
                created_at=report.created_at,
                source_name=report.user_name,
                source_role=report.user_role,
                description=report.description,
                source_reliability=report.reliability_score,
                location_name=report.location_name,
                status="Conflicting" if conflicting else _status_label(report, reports),
                incident_type=report.incident_type,
                conflicting=conflicting,
            )
        )
    return items


def _status_label(report: SignalInput, cohort: list[SignalInput]) -> str:
    others = [item for item in cohort if item.id != report.id and item.user_id != report.user_id]
    if others:
        return "Corroborated"
    if report.is_official:
        return "Official"
    return "Unconfirmed"


def assess_signals(
    reports: list[SignalInput],
    now: datetime | None = None,
    cfg: Settings | None = None,
    geometry: list[tuple[float, float]] | None = None,
    route_name: str = "",
) -> AssessmentResult:
    cfg = cfg or settings
    moment = now or utc_now()

    relevant = reports
    if geometry is not None:
        relevant = [report for report in reports if report_affects_route(report, geometry, route_name, cfg)]

    live = active_reports(relevant, moment, cfg)
    relationships = build_relationships(live, now=moment, cfg=cfg)

    hazards = [report for report in live if report.incident_type in HAZARD_TYPES]
    clears = [report for report in live if report.incident_type in CLEAR_TYPES]

    contradict_ids: set[str] = set()
    for rel in relationships:
        if rel.relationship_type == REL_CONTRADICTS:
            contradict_ids.add(rel.report_id)
            contradict_ids.add(rel.related_report_id)

    contradicting = [
        report
        for report in live
        if report.id in contradict_ids and report.incident_type in CLEAR_TYPES
    ]
    # Also treat nearby all-clear reports as contradictions against a hazard cluster.
    if hazards:
        extra = [
            report
            for report in clears
            if any(location_related(report, hazard, cfg) for hazard in hazards)
        ]
        seen = {item.id for item in contradicting}
        for report in extra:
            if report.id not in seen:
                contradicting.append(report)

    clusters = cluster_reports(hazards, cfg) if hazards else []
    primary = max(clusters, key=len) if clusters else []

    scores = compute_confidence(primary, contradicting, now=moment, cfg=cfg) if primary else None
    state = decide_state(primary, clears, scores, cfg)

    last_updated = None
    if live:
        last_updated = max((as_utc(report.created_at) for report in live), default=None)

    latest_age = age_minutes(last_updated, moment) if last_updated else None
    freshness = (
        FRESHNESS_LABELS[freshness_band(latest_age, cfg)] if latest_age is not None else "No recent updates"
    )

    if state == STATE_CLEAR:
        confidence = 0.62 if any(report.is_official for report in clears) else 0.58
        scores = scores or ScoreBreakdown(0.0, 0.0, 1.0, 0.0, 0.0, 0.0, confidence, confidence)
        # CLEAR is a positive finding, not a default. Keep confidence modest and explicit.
        factors = build_factors(clears, [], scores, any(r.is_official for r in clears), now=moment)
        result = AssessmentResult(
            state=state,
            confidence=round(confidence, 4),
            headline=HEADLINES[state],
            reason=reason_for(state),
            last_updated=last_updated,
            recent_reports=len(clears),
            independent_sources=len(independent_source_ids(clears)),
            official_confirmation=any(report.is_official for report in clears),
            freshness_label=freshness,
            factors=factors,
            reports=_to_evidence(clears),
            conflicting=[],
            scores=scores,
            relationships=relationships,
        )
        return attach_copy(result)

    if state == STATE_UNKNOWN or not scores:
        empty = ScoreBreakdown(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        result = AssessmentResult(
            state=STATE_UNKNOWN,
            confidence=0.0,
            headline=HEADLINES[STATE_UNKNOWN],
            reason=reason_for(STATE_UNKNOWN),
            last_updated=last_updated,
            recent_reports=0,
            independent_sources=0,
            official_confirmation=False,
            freshness_label="No recent updates",
            factors=build_factors([], [], empty, False, now=moment),
            reports=[],
            conflicting=[],
            scores=empty,
            relationships=relationships,
        )
        return attach_copy(result)

    location = primary[0].location_name if primary else None
    result = AssessmentResult(
        state=state,
        confidence=scores.confidence,
        headline=HEADLINES[state],
        reason=reason_for(state),
        last_updated=last_updated,
        recent_reports=len(primary),
        independent_sources=len(independent_source_ids(primary)),
        official_confirmation=any(report.is_official for report in primary),
        freshness_label=freshness if last_updated else "No recent updates",
        factors=build_factors(primary, contradicting, scores, any(r.is_official for r in primary), now=moment),
        reports=_to_evidence(primary),
        conflicting=_to_evidence(contradicting, conflicting=True),
        scores=scores,
        relationships=relationships,
        cluster_location=location,
    )
    return attach_copy(result)


def human_updated_label(last_updated: datetime | None, now: datetime | None = None) -> str | None:
    if last_updated is None:
        return None
    return minutes_label(age_minutes(last_updated, now))
