from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from app.core.config import Settings, settings


class FreshnessBand(str, Enum):
    VERY_FRESH = "very_fresh"
    FRESH = "fresh"
    AGING = "aging"
    STALE = "stale"
    EXPIRED = "expired"


FRESHNESS_LABELS = {
    FreshnessBand.VERY_FRESH: "Very fresh",
    FreshnessBand.FRESH: "Fresh",
    FreshnessBand.AGING: "Aging",
    FreshnessBand.STALE: "Stale",
    FreshnessBand.EXPIRED: "Expired",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def age_minutes(created_at: datetime, now: datetime | None = None) -> float:
    moment = as_utc(now or utc_now())
    return max(0.0, (moment - as_utc(created_at)).total_seconds() / 60.0)


def freshness_band(age: float, cfg: Settings | None = None) -> FreshnessBand:
    cfg = cfg or settings
    if age >= cfg.report_expiry_minutes:
        return FreshnessBand.EXPIRED
    if age <= cfg.freshness_very_fresh_minutes:
        return FreshnessBand.VERY_FRESH
    if age <= cfg.freshness_fresh_minutes:
        return FreshnessBand.FRESH
    if age <= cfg.freshness_aging_minutes:
        return FreshnessBand.AGING
    return FreshnessBand.STALE


def freshness_score(age: float, cfg: Settings | None = None) -> float:
    """Piecewise linear decay. Thresholds come from settings, not literals in callers."""
    cfg = cfg or settings
    very = cfg.freshness_very_fresh_minutes
    fresh = cfg.freshness_fresh_minutes
    aging = cfg.freshness_aging_minutes
    expired = cfg.report_expiry_minutes

    if age <= very:
        return 1.0
    if age <= fresh:
        return _lerp(age, very, fresh, 1.0, 0.70)
    if age <= aging:
        return _lerp(age, fresh, aging, 0.70, 0.35)
    if age < expired:
        return _lerp(age, aging, expired, 0.35, 0.0)
    return 0.0


def is_expired(age: float, cfg: Settings | None = None) -> bool:
    cfg = cfg or settings
    return age >= cfg.report_expiry_minutes


def _lerp(value: float, left: float, right: float, start: float, end: float) -> float:
    if right == left:
        return end
    t = (value - left) / (right - left)
    return start + (end - start) * t
