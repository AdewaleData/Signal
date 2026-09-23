from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.db.seed import seed_if_empty
from app.db.session import Base, SessionLocal, engine
from app.models import Report, ReportRelationship, Route, RouteAssessment, RouteSegment, User  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Signal",
    description="Community signal verification and route assessment. This prototype does not guarantee physical safety.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "service": "signal"}


@app.get("/api/me")
def me() -> dict:
    return {
        "id": "user-amara",
        "name": "Amara Okafor",
        "role": "Shop Owner",
        "town": "Aderin",
        "reliability_score": 0.75,
    }
