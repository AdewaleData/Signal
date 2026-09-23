from __future__ import annotations

import re
from itertools import combinations

from app.core.config import Settings, settings
from app.core.locations import places_share_road, resolve_place
from app.services.freshness import age_minutes
from app.services.geo import haversine_meters
from app.services.types import (
    CLEAR_TYPES,
    HAZARD_TYPES,
    REL_CONTRADICTS,
    REL_CORROBORATES,
    REL_UNRELATED,
    RelationshipResult,
    SignalInput,
)

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "near",
    "from",
    "my",
    "is",
    "are",
    "cannot",
    "can",
    "not",
}

HAZARD_CUES = {
    "block",
    "blocked",
    "blockage",
    "closed",
    "stop",
    "stopped",
    "cannot pass",
    "nobody fit pass",
    "no go",
    "crowd",
    "gathering",
    "accident",
    "fire",
    "gun",
    "security",
    "incident",
}

CLEAR_CUES = {
    "clear",
    "open",
    "passable",
    "quiet",
    "normal",
    "nothing happening",
    "no problem",
    "road appears clear",
    "vehicles passing",
}


def tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def text_similarity(a: str, b: str) -> float:
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def has_cues(text: str, cues: set[str]) -> bool:
    lowered = text.lower()
    return any(cue in lowered for cue in cues)


def types_oppose(a: SignalInput, b: SignalInput) -> bool:
    a_clear = a.incident_type in CLEAR_TYPES or has_cues(a.description, CLEAR_CUES)
    b_clear = b.incident_type in CLEAR_TYPES or has_cues(b.description, CLEAR_CUES)
    a_hazard = a.incident_type in HAZARD_TYPES or has_cues(a.description, HAZARD_CUES)
    b_hazard = b.incident_type in HAZARD_TYPES or has_cues(b.description, HAZARD_CUES)
    return (a_clear and b_hazard) or (b_clear and a_hazard)


def types_similar(a: SignalInput, b: SignalInput) -> bool:
    if a.incident_type == b.incident_type:
        return True
    related = {
        frozenset({"road_blocked", "crowd_gathering"}),
        frozenset({"road_blocked", "security_incident"}),
        frozenset({"crowd_gathering", "security_incident"}),
    }
    return frozenset({a.incident_type, b.incident_type}) in related


def location_related(a: SignalInput, b: SignalInput, cfg: Settings | None = None) -> bool:
    cfg = cfg or settings
    place_a, place_b = resolve_place(a.location_name), resolve_place(b.location_name)
    if place_a and place_b:
        if place_a.key == place_b.key:
            return True
        if not places_share_road(place_a, place_b):
            return False
    distance = haversine_meters(a.latitude, a.longitude, b.latitude, b.longitude)
    return distance <= cfg.location_cluster_meters


def classify_pair(
    a: SignalInput,
    b: SignalInput,
    now=None,
    cfg: Settings | None = None,
) -> RelationshipResult:
    cfg = cfg or settings
    time_gap = abs(age_minutes(a.created_at, now) - age_minutes(b.created_at, now))
    near_in_time = time_gap <= cfg.corroboration_time_window_minutes
    similar_text = text_similarity(a.description, b.description)
    related_place = location_related(a, b, cfg)

    if types_oppose(a, b) and related_place and near_in_time:
        score = max(0.55, 0.70 - similar_text * 0.1)
        return RelationshipResult(a.id, b.id, REL_CONTRADICTS, round(score, 3))

    if related_place and near_in_time and types_similar(a, b):
        score = 0.45 + 0.40 * similar_text
        if a.incident_type == b.incident_type:
            score += 0.10
        return RelationshipResult(a.id, b.id, REL_CORROBORATES, round(min(1.0, score), 3))

    return RelationshipResult(a.id, b.id, REL_UNRELATED, round(similar_text, 3))


def build_relationships(
    reports: list[SignalInput],
    now=None,
    cfg: Settings | None = None,
) -> list[RelationshipResult]:
    results: list[RelationshipResult] = []
    for left, right in combinations(reports, 2):
        results.append(classify_pair(left, right, now=now, cfg=cfg))
    return results


def cluster_reports(
    reports: list[SignalInput],
    cfg: Settings | None = None,
) -> list[list[SignalInput]]:
    """Group reports that share a road/place. Different roads stay separate."""
    cfg = cfg or settings
    if not reports:
        return []

    parent = {report.id: report.id for report in reports}

    def find(node: str) -> str:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for left, right in combinations(reports, 2):
        if location_related(left, right, cfg) and types_similar(left, right):
            union(left.id, right.id)

    buckets: dict[str, list[SignalInput]] = {}
    by_id = {report.id: report for report in reports}
    for report_id in parent:
        buckets.setdefault(find(report_id), []).append(by_id[report_id])
    return list(buckets.values())
