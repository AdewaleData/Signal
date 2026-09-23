from pydantic import BaseModel, Field

from app.services.types import INCIDENT_TYPES


class NormalizedReport(BaseModel):
    incident_type: str
    location_reference: str
    description: str = Field(..., min_length=3, max_length=400)
    confidence: float = Field(ge=0.0, le=1.0)

    def validated_type(self) -> str:
        if self.incident_type not in INCIDENT_TYPES:
            return "other"
        return self.incident_type
