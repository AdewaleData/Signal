from datetime import datetime, timedelta, timezone

from app.core.config import Settings, normalize_database_url
from app.core.locations import PLACES
from app.services.assessment import assess_signals, report_affects_route
from app.services.confidence import compute_confidence, independent_source_ids
from app.services.corroboration import classify_pair, cluster_reports
from app.services.freshness import freshness_score
from app.services.types import REL_CONTRADICTS, REL_UNRELATED, STATE_AVOID, STATE_CAUTION, STATE_CLEAR, STATE_UNKNOWN, SignalInput

CFG = Settings()
NOW = datetime(2026, 9, 23, 18, 40, tzinfo=timezone.utc)


def _report(
    report_id: str,
    user_id: str,
    *,
    place: str = "pharmacy",
    incident: str = "road_blocked",
    minutes: int = 3,
    reliability: float = 0.72,
    role: str = "Resident",
    description: str = "Vehicles cannot pass near the pharmacy.",
    quality: float = 0.48,
    official: bool = False,
    location_name: str | None = None,
) -> SignalInput:
    spot = PLACES[place]
    return SignalInput(
        id=report_id,
        user_id=user_id,
        user_name=user_id,
        user_role=role,
        reliability_score=reliability,
        incident_type=incident,
        description=description,
        latitude=spot.latitude,
        longitude=spot.longitude,
        location_name=location_name or spot.name,
        created_at=NOW - timedelta(minutes=minutes),
        evidence_quality=quality,
        is_official=official,
    )


def test_no_reports_is_unknown():
    result = assess_signals([], now=NOW, cfg=CFG)
    assert result.state == STATE_UNKNOWN
    assert result.confidence == 0.0


def test_no_evidence_does_not_become_clear():
    result = assess_signals([], now=NOW, cfg=CFG)
    assert result.state != STATE_CLEAR
    assert "enough" in result.reason.lower() or "information" in result.reason.lower()


def test_one_fresh_weak_report_is_caution():
    report = _report("r1", "u1", reliability=0.40, role="Anonymous User", quality=0.30)
    result = assess_signals([report], now=NOW, cfg=CFG)
    assert result.state == STATE_CAUTION
    assert result.independent_sources == 1
    assert result.confidence < CFG.avoid_confidence_threshold


def test_multiple_independent_reports_raise_confidence():
    one = _report("r1", "u1", reliability=0.72)
    two = _report("r2", "u2", minutes=4, reliability=0.87, role="Community Volunteer")
    single = compute_confidence([one], now=NOW, cfg=CFG)
    pair = compute_confidence([one, two], now=NOW, cfg=CFG)
    assert pair.confidence > single.confidence
    assert pair.corroboration > single.corroboration


def test_strong_corroboration_is_avoid():
    reports = [
        _report("r1", "volunteer", reliability=0.87, role="Community Volunteer", minutes=6, quality=0.55),
        _report("r2", "resident", reliability=0.72, role="Resident", minutes=3, quality=0.50),
        _report(
            "r3",
            "responder",
            reliability=0.93,
            role="Local Responder",
            minutes=2,
            quality=0.78,
            official=True,
            description="Confirmed blockage beside the pharmacy.",
        ),
    ]
    result = assess_signals(reports, now=NOW, cfg=CFG)
    assert result.state == STATE_AVOID
    assert result.independent_sources >= 2
    assert result.confidence >= CFG.avoid_confidence_threshold


def test_old_reports_reduce_confidence():
    fresh = [
        _report("r1", "u1", minutes=4, reliability=0.87),
        _report("r2", "u2", minutes=3, reliability=0.72),
    ]
    aging = [
        _report("r1", "u1", minutes=50, reliability=0.87),
        _report("r2", "u2", minutes=48, reliability=0.72),
    ]
    fresh_score = compute_confidence(fresh, now=NOW, cfg=CFG)
    aging_score = compute_confidence(aging, now=NOW, cfg=CFG)
    assert aging_score.recency < fresh_score.recency
    assert aging_score.confidence < fresh_score.confidence


def test_contradictory_evidence_reduces_confidence():
    hazards = [
        _report("r1", "u1", reliability=0.87, role="Community Volunteer"),
        _report("r2", "u2", minutes=4, reliability=0.72),
    ]
    contradiction = _report(
        "r3",
        "u3",
        incident="all_clear",
        minutes=2,
        reliability=0.70,
        description="Road appears clear from my location.",
    )
    base = compute_confidence(hazards, now=NOW, cfg=CFG)
    penalized = compute_confidence(hazards, [contradiction], now=NOW, cfg=CFG)
    assert penalized.confidence < base.confidence
    assert penalized.contradiction_penalty > 0


def test_same_source_is_not_independent():
    reports = [
        _report("r1", "same-person", minutes=8),
        _report("r2", "same-person", minutes=5, description="Still blocked near the pharmacy."),
        _report("r3", "same-person", minutes=2, description="Road remains blocked."),
    ]
    assert independent_source_ids(reports) == ["same-person"]
    result = assess_signals(reports, now=NOW, cfg=CFG)
    assert result.independent_sources == 1
    assert result.state != STATE_AVOID


def test_different_locations_are_not_grouped():
    market = _report("r1", "u1", place="pharmacy", location_name="Market Road")
    station = _report("r2", "u2", place="bus_station", location_name="Station Road")
    clusters = cluster_reports([market, station], CFG)
    assert len(clusters) == 2
    rel = classify_pair(market, station, now=NOW, cfg=CFG)
    assert rel.relationship_type == REL_UNRELATED


def test_expired_incidents_are_ignored():
    expired = _report("r1", "u1", minutes=CFG.report_expiry_minutes + 15, reliability=0.93)
    result = assess_signals([expired], now=NOW, cfg=CFG)
    assert result.state == STATE_UNKNOWN
    assert result.recent_reports == 0


def test_contradiction_relationship_is_detected():
    blocked = _report("r1", "u1")
    clear = _report(
        "r2",
        "u2",
        incident="all_clear",
        description="Road appears clear from my location.",
    )
    rel = classify_pair(blocked, clear, now=NOW, cfg=CFG)
    assert rel.relationship_type == REL_CONTRADICTS


def test_official_all_clear_can_produce_clear():
    clear = _report(
        "c1",
        "responder",
        place="river_bridge",
        incident="all_clear",
        reliability=0.93,
        official=True,
        description="River Road is open. Traffic is moving normally.",
        location_name="River Road",
    )
    result = assess_signals([clear], now=NOW, cfg=CFG)
    assert result.state == STATE_CLEAR


def test_named_road_is_not_assigned_by_proximity():
    river = _report(
        "r1",
        "responder",
        place="river_bridge",
        incident="all_clear",
        official=True,
        reliability=0.93,
        location_name="River Road",
        description="River Road is open.",
    )
    central = _report(
        "r2",
        "volunteer",
        place="community_centre",
        incident="all_clear",
        location_name="Central Avenue",
        description="Central Avenue is quiet.",
    )
    geometry = [
        (PLACES["shop"].latitude, PLACES["shop"].longitude),
        (PLACES["river_bridge"].latitude, PLACES["river_bridge"].longitude),
        (PLACES["community_centre"].latitude, PLACES["community_centre"].longitude),
        (PLACES["home"].latitude, PLACES["home"].longitude),
    ]
    assert report_affects_route(river, geometry, "River Road", CFG)
    assert not report_affects_route(central, geometry, "River Road", CFG)


def test_reports_on_another_road_do_not_affect_route():
    market = _report("r1", "u1", place="pharmacy", location_name="Market Road")
    station = _report("r2", "u2", place="bus_station", location_name="Station Road")
    geometry = [
        (PLACES["shop"].latitude, PLACES["shop"].longitude),
        (PLACES["market"].latitude, PLACES["market"].longitude),
        (PLACES["home"].latitude, PLACES["home"].longitude),
    ]
    assert report_affects_route(market, geometry, "Market Road", CFG)
    assert not report_affects_route(station, geometry, "Market Road", CFG)
    result = assess_signals([market, station], now=NOW, cfg=CFG, geometry=geometry, route_name="Market Road")
    assert result.recent_reports == 1
    assert result.state == STATE_CAUTION


def test_render_database_url_is_normalized():
    url = normalize_database_url("postgres://signal:pass@dpg-host/signal")
    assert url.startswith("postgresql+psycopg://")
    assert "sslmode=require" in url


def test_freshness_thresholds_are_configurable():
    assert freshness_score(5, CFG) == 1.0
    assert freshness_score(20, CFG) < 1.0
    assert freshness_score(45, CFG) < freshness_score(20, CFG)
    assert freshness_score(CFG.report_expiry_minutes, CFG) == 0.0
