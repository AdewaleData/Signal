from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.serializers import assessment_to_out, report_to_out
from app.core.ids import ROUTE_SHOP_HOME, USER_ANON, USER_FATIMA, USER_NGOZI
from app.core.locations import PLACES
from app.db.seed import new_id, reset_demo
from app.db.session import get_db
from app.models import Report, Route, User
from app.schemas.assessment import AssessmentOut
from app.services.assessment import assess_signals, parse_geometry
from app.services.pipeline import recompute_all_routes, signals_from_db

router = APIRouter(prefix="/api/demo", tags=["demo"])


def _shop_home(db: Session) -> Route:
    route = db.scalar(select(Route).options(joinedload(Route.segments)).where(Route.id == ROUTE_SHOP_HOME))
    if not route:
        raise HTTPException(status_code=404, detail="Demo route missing")
    return route


def _assessment(db: Session, route: Route) -> AssessmentOut:
    result = assess_signals(signals_from_db(db), geometry=parse_geometry(route.geometry), route_name=route.name)
    sibling = db.scalar(select(Route.id).where(Route.alternate_of == route.id))
    return assessment_to_out(route, result, sibling)


def _add_report(
    db: Session,
    *,
    user_id: str,
    incident_type: str,
    description: str,
    location_name: str,
    official: bool,
    quality: float,
) -> Report:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=500, detail="Demo user missing")
    place = PLACES["pharmacy"]
    report = Report(
        id=new_id("demo"),
        user_id=user.id,
        incident_type=incident_type,
        description=description,
        latitude=place.latitude + 0.00012,
        longitude=place.longitude - 0.00008,
        location_name=location_name,
        created_at=datetime.now(timezone.utc),
        status="active",
        severity="high" if incident_type != "all_clear" else "low",
        evidence_quality=quality,
        is_official=official,
    )
    db.add(report)
    user.reports_count += 1
    db.commit()
    return db.scalar(select(Report).options(joinedload(Report.user)).where(Report.id == report.id))


@router.post("/reset")
def demo_reset(db: Session = Depends(get_db)) -> dict:
    reset_demo(db)
    route = _shop_home(db)
    return {"ok": True, "assessment": _assessment(db, route).model_dump(mode="json")}


@router.post("/simulate-report")
def simulate_report(db: Session = Depends(get_db)) -> dict:
    """Add a third independent corroborating report. Expected: CAUTION → AVOID."""
    report = _add_report(
        db,
        user_id=USER_FATIMA,
        incident_type="road_blocked",
        description="Confirmed: vehicles still cannot pass beside the pharmacy on Market Road.",
        location_name="Market Road",
        official=True,
        quality=0.78,
    )
    recompute_all_routes(db)
    return {
        "report": report_to_out(report).model_dump(mode="json"),
        "assessment": _assessment(db, _shop_home(db)).model_dump(mode="json"),
        "note": "A new independent corroborating report was added. The engine re-evaluated the route.",
    }


@router.post("/confirm-report")
def confirm_report(db: Session = Depends(get_db)) -> dict:
    report = _add_report(
        db,
        user_id=USER_FATIMA,
        incident_type="road_blocked",
        description="Official confirmation: Market Road remains blocked near the pharmacy.",
        location_name="Market Road",
        official=True,
        quality=0.82,
    )
    recompute_all_routes(db)
    return {
        "report": report_to_out(report).model_dump(mode="json"),
        "assessment": _assessment(db, _shop_home(db)).model_dump(mode="json"),
        "note": "Official confirmation was added. The engine re-evaluated the route.",
    }


@router.post("/contradict-report")
def contradict_report(db: Session = Depends(get_db)) -> dict:
    """Add a conflicting all-clear. Expected: AVOID → CAUTION when contradiction is strong."""
    report = _add_report(
        db,
        user_id=USER_NGOZI if db.get(User, USER_NGOZI) else USER_ANON,
        incident_type="all_clear",
        description="Road appears clear from my location.",
        location_name="Market Road",
        official=False,
        quality=0.42,
    )
    recompute_all_routes(db)
    return {
        "report": report_to_out(report).model_dump(mode="json"),
        "assessment": _assessment(db, _shop_home(db)).model_dump(mode="json"),
        "note": "A conflicting signal was added. Contradictory evidence reduces confidence.",
    }


@router.get("/scenario")
def demo_scenario(db: Session = Depends(get_db)) -> dict:
    route = _shop_home(db)
    return {
        "town": "Aderin",
        "time": "18:40",
        "user": "Amara Okafor",
        "question": "Is the road home safe enough to take right now?",
        "route": {"id": route.id, "origin": route.origin, "destination": route.destination},
        "assessment": _assessment(db, route).model_dump(mode="json"),
    }
