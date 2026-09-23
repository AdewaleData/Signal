from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    incident_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    location_name: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="medium")
    evidence_quality: Mapped[float] = mapped_column(Float, nullable=False, default=0.45)
    is_official: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="reports")


class ReportRelationship(Base):
    __tablename__ = "report_relationships"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    report_id: Mapped[str] = mapped_column(String(64), ForeignKey("reports.id"), nullable=False, index=True)
    related_report_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("reports.id"), nullable=False, index=True
    )
    relationship_type: Mapped[str] = mapped_column(String(32), nullable=False)
    similarity_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
