"""Optional LLM normalizer. Never decides safety. Always validated with Pydantic."""

from __future__ import annotations

import json
import re

import httpx

from app.core.config import settings
from app.core.locations import PLACES, resolve_place
from app.schemas.ai import NormalizedReport
from app.services.types import INCIDENT_TYPES

TYPE_KEYWORDS = {
    "road_blocked": (
        "block",
        "blocked",
        "blockage",
        "cannot pass",
        "nobody fit pass",
        "don block",
        "closed",
        "no go",
        "vehicles cannot",
    ),
    "crowd_gathering": ("crowd", "gathering", "people blocking", "protest", "mob"),
    "accident": ("accident", "crash", "collision", "knock"),
    "fire": ("fire", "smoke", "burning"),
    "security_incident": ("security", "gun", "shooting", "raid", "vigilante"),
    "all_clear": ("clear", "open", "passable", "nothing happening", "quiet", "normal"),
}


SYSTEM_PROMPT = """You extract structured fields from a local incident report.
Return JSON only with keys: incident_type, location_reference, description, confidence.
incident_type must be one of: road_blocked, crowd_gathering, accident, fire, security_incident, other, all_clear.
Normalize informal or pidgin language into plain English.
Do not decide if a road is safe. Do not invent places, people, or confirmations.
If the location is unclear, use "unknown".
confidence is how sure you are about the extraction, from 0 to 1.
"""


def normalize_report(text: str) -> NormalizedReport:
    cleaned = text.strip()
    if settings.llm_enabled:
        try:
            return _normalize_with_llm(cleaned)
        except Exception:
            return _normalize_with_rules(cleaned)
    return _normalize_with_rules(cleaned)


def _normalize_with_rules(text: str) -> NormalizedReport:
    lowered = text.lower()
    incident = "other"
    for kind, keywords in TYPE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            incident = kind
            break

    place = resolve_place(text)
    location = place.name.lower() if place else "unknown"
    if location == "unknown":
        for key, item in PLACES.items():
            if key.replace("_", " ") in lowered or item.name.lower() in lowered:
                location = item.name.lower()
                break

    description = _plain_english(text, incident, location)
    return NormalizedReport(
        incident_type=incident,
        location_reference=location,
        description=description,
        confidence=0.62 if incident != "other" else 0.4,
    )


def _plain_english(text: str, incident: str, location: str) -> str:
    if incident == "road_blocked":
        where = location if location != "unknown" else "the reported area"
        return f"Road reportedly blocked and vehicles cannot pass near {where}."
    if incident == "all_clear":
        return f"Observer says the road near {location} appears clear."
    if incident == "crowd_gathering":
        return f"Crowd or gathering reported near {location}."
    compact = re.sub(r"\s+", " ", text).strip()
    if compact.endswith("."):
        return compact
    return compact[:240] + ("." if len(compact) < 240 else "")


def _normalize_with_llm(text: str) -> NormalizedReport:
    payload = {
        "model": settings.openai_model,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    response = httpx.post(
        f"{settings.openai_base_url.rstrip('/')}/chat/completions",
        headers=headers,
        json=payload,
        timeout=12.0,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    raw = json.loads(content)
    parsed = NormalizedReport.model_validate(raw)
    if parsed.incident_type not in INCIDENT_TYPES:
        parsed.incident_type = "other"
    return parsed
