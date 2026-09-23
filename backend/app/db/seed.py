from __future__ import annotations

import json
from datetime import timedelta
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.ids import (
    REPORT_CENTRAL_CLEAR,
    REPORT_CENTRAL_CLEAR_2,
    REPORT_MARKET_1,
    REPORT_MARKET_2,
    REPORT_RIVER_CLEAR,
    REPORT_STATION_1,
    REPORT_STATION_2,
    REPORT_STATION_3,
    ROUTE_CENTRAL,
    ROUTE_HILL,
    ROUTE_SHOP_HOME,
    ROUTE_SHOP_HOME_ALT,
    ROUTE_STATION,
    USER_AMARA,
    USER_AMINA,
    USER_ANON,
    USER_CHIDI,
    USER_EMEKA,
    USER_FATIMA,
    USER_IBRAHIM,
    USER_NGOZI,
)
from app.core.locations import PLACES
from app.models import Report, ReportRelationship, Route, RouteAssessment, RouteSegment, User
from app.services.assessment import assess_signals, parse_geometry
from app.services.freshness import utc_now
from app.services.pipeline import persist_assessment, persist_relationships, signals_from_db

USERS = [
    {
        "id": USER_AMARA,
        "name": "Amara Okafor",
        "role": "Shop Owner",
        "reliability_score": 0.75,
        "reports_count": 4,
        "confirmed_reports": 2,
    },
    {
        "id": USER_CHIDI,
        "name": "Chidi Nwosu",
        "role": "Community Volunteer",
        "reliability_score": 0.87,
        "reports_count": 18,
        "confirmed_reports": 14,
    },
    {
        "id": USER_FATIMA,
        "name": "Fatima Bello",
        "role": "Local Responder",
        "reliability_score": 0.93,
        "reports_count": 31,
        "confirmed_reports": 28,
    },
    {
        "id": USER_EMEKA,
        "name": "Emeka Adeyemi",
        "role": "Resident",
        "reliability_score": 0.72,
        "reports_count": 7,
        "confirmed_reports": 4,
    },
    {
        "id": USER_NGOZI,
        "name": "Ngozi Eze",
        "role": "Resident",
        "reliability_score": 0.70,
        "reports_count": 5,
        "confirmed_reports": 3,
    },
    {
        "id": USER_ANON,
        "name": "Anonymous User",
        "role": "Anonymous User",
        "reliability_score": 0.40,
        "reports_count": 2,
        "confirmed_reports": 0,
    },
    {
        "id": USER_IBRAHIM,
        "name": "Ibrahim Sule",
        "role": "Local Responder",
        "reliability_score": 0.91,
        "reports_count": 22,
        "confirmed_reports": 19,
    },
    {
        "id": USER_AMINA,
        "name": "Amina Yusuf",
        "role": "Community Volunteer",
        "reliability_score": 0.85,
        "reports_count": 12,
        "confirmed_reports": 9,
    },
]


def _line(*keys: str) -> str:
    points = [[PLACES[key].latitude, PLACES[key].longitude] for key in keys]
    return json.dumps(points)


def _segments(route_id: str, keys: list[str]) -> list[RouteSegment]:
    segments = []
    for index, key in enumerate(keys):
        place = PLACES[key]
        segments.append(
            RouteSegment(
                id=f"{route_id}-seg-{index}",
                route_id=route_id,
                name=place.name,
                sequence=index,
                latitude=place.latitude,
                longitude=place.longitude,
            )
        )
    return segments


def seed_if_empty(db: Session) -> None:
    existing = db.scalar(select(User.id).limit(1))
    if existing:
        refresh_demo_clock(db)
        return
    seed_all(db)


def reset_demo(db: Session) -> None:
    db.query(RouteAssessment).delete()
    db.query(ReportRelationship).delete()
    db.query(Report).delete()
    db.query(RouteSegment).delete()
    db.query(Route).delete()
    db.query(User).delete()
    db.commit()
    seed_all(db)


def seed_all(db: Session) -> None:
    now = utc_now()

    for payload in USERS:
        db.add(User(**payload))

    routes = [
        Route(
            id=ROUTE_SHOP_HOME,
            name="Market Road",
            origin="Shop",
            destination="Home",
            geometry=_line("shop", "market", "pharmacy", "home"),
            estimated_minutes=10,
            distance_km=2.1,
            alternate_of=None,
        ),
        Route(
            id=ROUTE_SHOP_HOME_ALT,
            name="River Road",
            origin="Shop",
            destination="Home",
            geometry=_line("shop", "river_bridge", "community_centre", "school", "home"),
            estimated_minutes=12,
            distance_km=2.4,
            alternate_of=ROUTE_SHOP_HOME,
        ),
        Route(
            id=ROUTE_STATION,
            name="Station Road",
            origin="Shop",
            destination="Bus Station",
            geometry=_line("shop", "bus_station"),
            estimated_minutes=7,
            distance_km=1.2,
        ),
        Route(
            id=ROUTE_CENTRAL,
            name="Central Avenue",
            origin="Shop",
            destination="Community Centre",
            geometry=_line("shop", "community_centre"),
            estimated_minutes=6,
            distance_km=0.9,
        ),
        Route(
            id=ROUTE_HILL,
            name="Hill Road",
            origin="Home",
            destination="School",
            geometry=_line("home", "school"),
            estimated_minutes=4,
            distance_km=0.5,
        ),
    ]
    db.add_all(routes)
    db.add_all(_segments(ROUTE_SHOP_HOME, ["shop", "market", "pharmacy", "home"]))
    db.add_all(_segments(ROUTE_SHOP_HOME_ALT, ["shop", "river_bridge", "community_centre", "school", "home"]))
    db.add_all(_segments(ROUTE_STATION, ["shop", "bus_station"]))
    db.add_all(_segments(ROUTE_CENTRAL, ["shop", "community_centre"]))
    db.add_all(_segments(ROUTE_HILL, ["home", "school"]))

    pharmacy = PLACES["pharmacy"]
    station = PLACES["bus_station"]
    river = PLACES["river_bridge"]
    centre = PLACES["community_centre"]

    db.add_all(
        [
            Report(
                id=REPORT_MARKET_1,
                user_id=USER_CHIDI,
                incident_type="road_blocked",
                description="Road blocked near the pharmacy.",
                latitude=pharmacy.latitude,
                longitude=pharmacy.longitude,
                location_name="Market Road",
                created_at=now - timedelta(minutes=6),
                status="active",
                severity="high",
                evidence_quality=0.50,
                is_official=False,
            ),
            Report(
                id=REPORT_MARKET_2,
                user_id=USER_EMEKA,
                incident_type="road_blocked",
                description="Vehicles cannot pass near the pharmacy.",
                latitude=pharmacy.latitude + 0.0002,
                longitude=pharmacy.longitude + 0.0001,
                location_name="Market Road",
                created_at=now - timedelta(minutes=3),
                status="active",
                severity="high",
                evidence_quality=0.48,
                is_official=False,
            ),
            Report(
                id=REPORT_STATION_1,
                user_id=USER_IBRAHIM,
                incident_type="crowd_gathering",
                description="Crowd blocking Station Road beside the bus park. Vehicles are being turned back.",
                latitude=station.latitude,
                longitude=station.longitude,
                location_name="Station Road",
                created_at=now - timedelta(minutes=12),
                status="active",
                severity="high",
                evidence_quality=0.70,
                is_official=True,
            ),
            Report(
                id=REPORT_STATION_2,
                user_id=USER_AMINA,
                incident_type="road_blocked",
                description="Station Road is closed. People gathered at the junction.",
                latitude=station.latitude + 0.00015,
                longitude=station.longitude - 0.0001,
                location_name="Station Road",
                created_at=now - timedelta(minutes=10),
                status="active",
                severity="high",
                evidence_quality=0.58,
                is_official=False,
            ),
            Report(
                id=REPORT_STATION_3,
                user_id=USER_NGOZI,
                incident_type="crowd_gathering",
                description="I cannot get through Station Road. The junction is fully blocked.",
                latitude=station.latitude - 0.0001,
                longitude=station.longitude + 0.00012,
                location_name="Station Road",
                created_at=now - timedelta(minutes=8),
                status="active",
                severity="high",
                evidence_quality=0.52,
                is_official=False,
            ),
            Report(
                id=REPORT_RIVER_CLEAR,
                user_id=USER_FATIMA,
                incident_type="all_clear",
                description="River Road is open. Traffic is moving normally toward the bridge.",
                latitude=river.latitude,
                longitude=river.longitude,
                location_name="River Road",
                created_at=now - timedelta(minutes=9),
                status="active",
                severity="low",
                evidence_quality=0.72,
                is_official=True,
            ),
            Report(
                id=REPORT_CENTRAL_CLEAR,
                user_id=USER_FATIMA,
                incident_type="all_clear",
                description="Central Avenue is quiet. No obstruction near the community centre.",
                latitude=centre.latitude,
                longitude=centre.longitude,
                location_name="Central Avenue",
                created_at=now - timedelta(minutes=14),
                status="active",
                severity="low",
                evidence_quality=0.70,
                is_official=True,
            ),
            Report(
                id=REPORT_CENTRAL_CLEAR_2,
                user_id=USER_AMINA,
                incident_type="all_clear",
                description="Just walked Central Avenue. Road is clear.",
                latitude=centre.latitude + 0.0001,
                longitude=centre.longitude - 0.00008,
                location_name="Central Avenue",
                created_at=now - timedelta(minutes=11),
                status="active",
                severity="low",
                evidence_quality=0.55,
                is_official=False,
            ),
        ]
    )
    db.commit()
    refresh_assessments(db)


def refresh_demo_clock(db: Session) -> None:
    """Keep the seeded story at 'a few minutes ago' every time the app starts."""
    now = utc_now()
    offsets = {
        REPORT_MARKET_1: 6,
        REPORT_MARKET_2: 3,
        REPORT_STATION_1: 12,
        REPORT_STATION_2: 10,
        REPORT_STATION_3: 8,
        REPORT_RIVER_CLEAR: 9,
        REPORT_CENTRAL_CLEAR: 14,
        REPORT_CENTRAL_CLEAR_2: 11,
    }
    reports = db.scalars(select(Report)).all()
    changed = False
    for report in reports:
        if report.id in offsets:
            report.created_at = now - timedelta(minutes=offsets[report.id])
            changed = True
        elif report.id.startswith("demo-"):
            # Leave live demo injections as-is so the judge can see change.
            continue
    if changed:
        db.commit()
        refresh_assessments(db)


def refresh_assessments(db: Session) -> None:
    db.query(ReportRelationship).delete()
    db.query(RouteAssessment).delete()
    db.commit()

    signals = signals_from_db(db)
    persist_relationships(db, signals)

    routes = db.scalars(select(Route)).all()
    for route in routes:
        geometry = parse_geometry(route.geometry)
        result = assess_signals(signals, geometry=geometry, route_name=route.name)
        persist_assessment(db, route.id, result)
    db.commit()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:10]}"
