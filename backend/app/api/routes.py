from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.serializers import assessment_to_out, evidence_to_out, route_to_out
from app.db.session import get_db
from app.models import Route
from app.schemas.assessment import AssessmentOut, EvidenceOut
from app.schemas.route import RouteListOut, RouteOut
from app.services.assessment import assess_signals, parse_geometry
from app.services.pipeline import signals_from_db

router = APIRouter(tags=["routes"])


def _load_route(db: Session, route_id: str) -> Route:
    route = db.scalar(select(Route).options(joinedload(Route.segments)).where(Route.id == route_id))
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


def _assess(db: Session, route: Route):
    signals = signals_from_db(db)
    return assess_signals(signals, geometry=parse_geometry(route.geometry), route_name=route.name)


def _alternate_id(db: Session, route: Route) -> str | None:
    if route.alternate_of:
        return route.alternate_of
    sibling = db.scalar(select(Route.id).where(Route.alternate_of == route.id))
    return sibling


@router.get("/api/routes", response_model=RouteListOut)
def list_routes(db: Session = Depends(get_db)) -> RouteListOut:
    routes = db.scalars(select(Route).options(joinedload(Route.segments))).unique().all()
    signals = signals_from_db(db)
    items: list[RouteOut] = []
    for route in routes:
        result = assess_signals(signals, geometry=parse_geometry(route.geometry), route_name=route.name)
        items.append(route_to_out(route, result))
    destinations = sorted({route.destination for route in routes})
    return RouteListOut(routes=items, destinations=destinations)


@router.get("/api/routes/{route_id}", response_model=RouteOut)
def get_route(route_id: str, db: Session = Depends(get_db)) -> RouteOut:
    route = _load_route(db, route_id)
    return route_to_out(route, _assess(db, route))


@router.get("/api/routes/{route_id}/assessment", response_model=AssessmentOut)
def get_assessment(route_id: str, db: Session = Depends(get_db)) -> AssessmentOut:
    route = _load_route(db, route_id)
    result = _assess(db, route)
    return assessment_to_out(route, result, _alternate_id(db, route))


@router.get("/api/routes/{route_id}/evidence", response_model=EvidenceOut)
def get_evidence(route_id: str, db: Session = Depends(get_db)) -> EvidenceOut:
    route = _load_route(db, route_id)
    result = _assess(db, route)
    return evidence_to_out(route, result, _alternate_id(db, route))
