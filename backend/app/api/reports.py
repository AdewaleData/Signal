from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.serializers import report_to_out
from app.core.config import settings
from app.core.ids import USER_AMARA
from app.core.locations import resolve_place
from app.db.seed import new_id
from app.db.session import get_db
from app.models import Report, User
from app.schemas.ai import NormalizedReport
from app.schemas.report import NormalizeRequest, ReportCreate, ReportOut
from app.services.ai_normalizer import normalize_report
from app.services.pipeline import recompute_all_routes
from app.services.types import INCIDENT_TYPES

router = APIRouter(tags=["reports"])


@router.get("/api/reports", response_model=list[ReportOut])
def list_reports(db: Session = Depends(get_db)) -> list[ReportOut]:
    reports = db.scalars(select(Report).options(joinedload(Report.user)).order_by(Report.created_at.desc())).all()
    return [report_to_out(report) for report in reports]


@router.get("/api/reports/{report_id}", response_model=ReportOut)
def get_report(report_id: str, db: Session = Depends(get_db)) -> ReportOut:
    report = db.scalar(select(Report).options(joinedload(Report.user)).where(Report.id == report_id))
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report_to_out(report)


@router.post("/api/reports", response_model=ReportOut, status_code=201)
def create_report(payload: ReportCreate, db: Session = Depends(get_db)) -> ReportOut:
    if payload.incident_type not in INCIDENT_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported incident type")

    user = db.get(User, settings.demo_user_id) or db.get(User, USER_AMARA)
    if not user:
        raise HTTPException(status_code=500, detail="Demo user is missing")

    place = resolve_place(payload.location_name)
    latitude = payload.latitude if payload.latitude is not None else (place.latitude if place else 6.4546)
    longitude = payload.longitude if payload.longitude is not None else (place.longitude if place else 3.4012)
    location_name = payload.location_name
    description = payload.description

    if payload.raw_text:
        normalized = normalize_report(payload.raw_text)
        if payload.incident_type == "other":
            payload.incident_type = normalized.validated_type()
        if not description:
            description = normalized.description

    report = Report(
        id=new_id("report"),
        user_id=user.id,
        incident_type=payload.incident_type,
        description=description,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        created_at=datetime.now(timezone.utc),
        status="active",
        severity="medium",
        evidence_quality=0.46,
        is_official=user.role == "Local Responder",
        raw_text=payload.raw_text,
    )
    db.add(report)
    user.reports_count += 1
    db.commit()
    db.refresh(report)
    report = db.scalar(select(Report).options(joinedload(Report.user)).where(Report.id == report.id))
    recompute_all_routes(db)
    return report_to_out(report)


@router.post("/api/reports/normalize", response_model=NormalizedReport)
def normalize_text(payload: NormalizeRequest) -> NormalizedReport:
    return normalize_report(payload.text)
