from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    origin: Mapped[str] = mapped_column(String(120), nullable=False)
    destination: Mapped[str] = mapped_column(String(120), nullable=False)
    geometry: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    alternate_of: Mapped[str | None] = mapped_column(String(64), ForeignKey("routes.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    segments = relationship("RouteSegment", back_populates="route", order_by="RouteSegment.sequence")
    assessments = relationship("RouteAssessment", back_populates="route")


class RouteSegment(Base):
    __tablename__ = "route_segments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    route_id: Mapped[str] = mapped_column(String(64), ForeignKey("routes.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    route = relationship("Route", back_populates="segments")


class RouteAssessment(Base):
    __tablename__ = "route_assessments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    route_id: Mapped[str] = mapped_column(String(64), ForeignKey("routes.id"), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    route = relationship("Route", back_populates="assessments")
