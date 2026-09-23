from __future__ import annotations

from app.services.freshness import FRESHNESS_LABELS, age_minutes, freshness_band
from app.services.types import (
    STATE_AVOID,
    STATE_CAUTION,
    STATE_CLEAR,
    STATE_UNKNOWN,
    AssessmentResult,
    FactorResult,
    ScoreBreakdown,
    SignalInput,
)


HEADLINES = {
    STATE_AVOID: "AVOID THIS ROUTE",
    STATE_CAUTION: "USE CAUTION",
    STATE_CLEAR: "ROUTE LOOKS CLEAR",
    STATE_UNKNOWN: "NOT ENOUGH INFORMATION",
}

REASONS = {
    STATE_AVOID: "Independent recent reports show an active incident. Use another route.",
    STATE_CAUTION: "Recent reports need attention. Evidence is incomplete.",
    STATE_CLEAR: "No active high-confidence incident on this route.",
    STATE_UNKNOWN: "Not enough reliable, recent information.",
}


def headline_for(state: str) -> str:
    return HEADLINES[state]


def reason_for(state: str) -> str:
    return REASONS[state]


def reliability_band(score: float) -> str:
    if score >= 0.85:
        return "High"
    if score >= 0.70:
        return "Medium-High"
    if score >= 0.55:
        return "Medium"
    return "Low"


def minutes_label(minutes: float) -> str:
    rounded = max(1, int(round(minutes)))
    if rounded < 60:
        return f"{rounded} minute{'s' if rounded != 1 else ''} ago"
    hours = rounded // 60
    return f"{hours} hour{'s' if hours != 1 else ''} ago"


def build_factors(
    reports: list[SignalInput],
    contradicting: list[SignalInput],
    scores: ScoreBreakdown,
    official: bool,
    now=None,
) -> list[FactorResult]:
    independent = {report.user_id for report in reports}
    latest_age = min((age_minutes(report.created_at, now) for report in reports), default=None)
    latest_label = minutes_label(latest_age) if latest_age is not None else "No recent reports"
    band = freshness_band(latest_age) if latest_age is not None else None

    location_ok = scores.location_agreement >= 0.75
    recency_ok = bool(reports) and scores.recency >= 0.70
    independent_ok = len(independent) >= 2
    reliability_ok = scores.source_reliability >= 0.65

    return [
        FactorResult(
            key="independent_reports",
            label="Independent reports",
            detail=(
                f"{len(independent)} from different people"
                if independent
                else "None"
            ),
            met=independent_ok,
            warning=not independent_ok,
            score=scores.corroboration,
        ),
        FactorResult(
            key="recency",
            label="Recency",
            detail=f"Latest {latest_label}"
            + (f", {FRESHNESS_LABELS[band].lower()}" if band else ""),
            met=recency_ok,
            warning=not recency_ok,
            score=scores.recency,
        ),
        FactorResult(
            key="location_agreement",
            label="Location",
            detail="Same area" if location_ok else "Locations do not match",
            met=location_ok,
            warning=not location_ok,
            score=scores.location_agreement,
        ),
        FactorResult(
            key="source_reliability",
            label="Reliability",
            detail=reliability_band(scores.source_reliability),
            met=reliability_ok,
            warning=not reliability_ok,
            score=scores.source_reliability,
        ),
        FactorResult(
            key="official_confirmation",
            label="Official",
            detail="Yes" if official else "None",
            met=official,
            warning=not official,
            score=1.0 if official else 0.0,
        ),
        FactorResult(
            key="contradiction",
            label="Conflicts",
            detail=(
                f"{len(contradicting)} conflicting report{'s' if len(contradicting) != 1 else ''}"
                if contradicting
                else "None"
            ),
            met=not contradicting,
            warning=bool(contradicting),
            score=scores.contradiction_penalty,
        ),
    ]


def attach_copy(result: AssessmentResult) -> AssessmentResult:
    result.headline = headline_for(result.state)
    result.reason = reason_for(result.state)
    if result.state == STATE_CAUTION and result.conflicting:
        result.reason = "Recent reports need attention, and at least one disagrees."
    if result.state == STATE_AVOID and result.official_confirmation:
        result.reason = "Recent reports, including official confirmation, show an active incident."
    return result
