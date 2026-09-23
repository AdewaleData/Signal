from __future__ import annotations

from collections.abc import Iterable

# Seeded demo roles. Historical corroboration can refine these later.
ROLE_RELIABILITY = {
    "Local Responder": 0.93,
    "Community Volunteer": 0.87,
    "Shop Owner": 0.75,
    "Resident": 0.72,
    "Anonymous User": 0.40,
    "Anonymous": 0.40,
}


def reliability_for_role(role: str, fallback: float = 0.50) -> float:
    return ROLE_RELIABILITY.get(role, fallback)


def average_unique_source_reliability(
    scores_by_user: Iterable[tuple[str, float]],
) -> float:
    """One vote per source. Repeat reports from the same person do not inflate reliability."""
    unique: dict[str, float] = {}
    for user_id, score in scores_by_user:
        unique[user_id] = score
    if not unique:
        return 0.0
    return sum(unique.values()) / len(unique)
