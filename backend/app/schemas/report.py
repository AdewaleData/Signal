from datetime import datetime

from pydantic import BaseModel, Field

from app.services.types import INCIDENT_TYPES


class ReportCreate(BaseModel):
    incident_type: str = Field(..., description="One of the supported incident types")
    description: str = Field(..., min_length=3, max_length=800)
    location_name: str = Field(..., min_length=2, max_length=120)
    latitude: float | None = None
    longitude: float | None = None
    raw_text: str | None = Field(default=None, max_length=800)

    def validate_type(self) -> str:
        if self.incident_type not in INCIDENT_TYPES:
            raise ValueError("Unsupported incident type")
        return self.incident_type


class ReportOut(BaseModel):
    id: str
    user_id: str
    user_name: str
    user_role: str
    incident_type: str
    description: str
    latitude: float
    longitude: float
    location_name: str
    created_at: datetime
    status: str
    severity: str
    source_reliability: float
    evidence_quality: float
    is_official: bool

    model_config = {"from_attributes": True}


class NormalizeRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=800)
