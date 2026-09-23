"""Prototype verification model.

confidence =
    0.25 * source_reliability
  + 0.25 * corroboration
  + 0.20 * recency
  + 0.20 * location_agreement
  + 0.10 * evidence_quality
  - contradiction_penalty

This is a screening-challenge prototype, not a validated safety model.
An LLM must never write these scores.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.core.config import Settings, settings
from app.core.locations import places_share_road, resolve_place
from app.services.freshness import age_minutes, freshness_score
from app.services.geo import haversine_meters
from app.services.reliability import average_unique_source_reliability
from app.services.types import ScoreBreakdown, SignalInput


def independent_source_ids(reports: Sequence[SignalInput]) -> list[str]:
    seen: list[str] = []
    for report in reports:
        if report.user_id not in seen:
            seen.append(report.user_id)
    return seen


def corroboration_score(independent_count: int) -> float:
    """Repeat reports from one person do not raise this score."""
    if independent_count <= 0:
        return 0.0
    if independent_count == 1:
        return 0.22
    if independent_count == 2:
        return 0.30
    if independent_count == 3:
        return 0.82
    return 0.95


def location_agreement_score(reports: Sequence[SignalInput], cfg: Settings | None = None) -> float:
    cfg = cfg or settings
    if not reports:
        return 0.0
    if len(reports) == 1:
        return 0.55

    scores: list[float] = []
    items = list(reports)
    for i, left in enumerate(items):
        for right in items[i + 1 :]:
            scores.append(_pair_location_score(left, right, cfg))
    return sum(scores) / len(scores) if scores else 0.0


def _pair_location_score(left: SignalInput, right: SignalInput, cfg: Settings) -> float:
    distance = haversine_meters(left.latitude, left.longitude, right.latitude, right.longitude)
    proximity = max(0.0, 1.0 - distance / max(cfg.location_cluster_meters, 1.0))
    place_a = resolve_place(left.location_name)
    place_b = resolve_place(right.location_name)
    if place_a and place_b:
        if place_a.key == place_b.key:
            return max(proximity, 0.92)
        if places_share_road(place_a, place_b):
            return max(proximity, 0.84)
        return min(proximity, 0.25)
    if left.location_name.strip().lower() == right.location_name.strip().lower():
        return max(proximity, 0.88)
    return proximity


def recency_score(reports: Sequence[SignalInput], now=None, cfg: Settings | None = None) -> float:
    cfg = cfg or settings
    if not reports:
        return 0.0
    newest = min(age_minutes(report.created_at, now) for report in reports)
    return freshness_score(newest, cfg)


def evidence_quality_score(reports: Sequence[SignalInput]) -> float:
    if not reports:
        return 0.0
    base = sum(report.evidence_quality for report in reports) / len(reports)
    if any(report.is_official for report in reports):
        base = min(1.0, base + 0.12)
    return base


def contradiction_penalty(
    contradicting: Sequence[SignalInput],
    cfg: Settings | None = None,
) -> float:
    cfg = cfg or settings
    if not contradicting:
        return 0.0
    unique = independent_source_ids(contradicting)
    avg_rel = average_unique_source_reliability(
        (report.user_id, report.reliability_score) for report in contradicting
    )
    penalty = 0.12 + 0.07 * len(unique) + 0.08 * avg_rel
    return min(cfg.contradiction_penalty_max, penalty)


def compute_confidence(
    reports: Sequence[SignalInput],
    contradicting: Sequence[SignalInput] | None = None,
    now=None,
    cfg: Settings | None = None,
) -> ScoreBreakdown:
    cfg = cfg or settings
    contradicting = list(contradicting or [])
    sources = independent_source_ids(reports)

    source_reliability = average_unique_source_reliability(
        (report.user_id, report.reliability_score) for report in reports
    )
    corroboration = corroboration_score(len(sources))
    recency = recency_score(reports, now=now, cfg=cfg)
    location_agreement = location_agreement_score(reports, cfg)
    evidence = evidence_quality_score(reports)
    penalty = contradiction_penalty(contradicting, cfg)

    raw = (
        cfg.weight_source_reliability * source_reliability
        + cfg.weight_corroboration * corroboration
        + cfg.weight_recency * recency
        + cfg.weight_location_agreement * location_agreement
        + cfg.weight_evidence_quality * evidence
    )
    confidence = max(0.0, min(1.0, raw - penalty))

    return ScoreBreakdown(
        source_reliability=round(source_reliability, 4),
        corroboration=round(corroboration, 4),
        recency=round(recency, 4),
        location_agreement=round(location_agreement, 4),
        evidence_quality=round(evidence, 4),
        contradiction_penalty=round(penalty, 4),
        raw_confidence=round(raw, 4),
        confidence=round(confidence, 4),
    )
