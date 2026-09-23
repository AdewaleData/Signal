from pydantic import BaseModel


class RoutePoint(BaseModel):
    name: str
    latitude: float
    longitude: float
    sequence: int


class RouteOut(BaseModel):
    id: str
    name: str
    origin: str
    destination: str
    estimated_minutes: int
    distance_km: float
    alternate_of: str | None
    geometry: list[list[float]]
    segments: list[RoutePoint]
    state: str | None = None
    confidence: float | None = None

    model_config = {"from_attributes": True}


class RouteListOut(BaseModel):
    routes: list[RouteOut]
    destinations: list[str]
