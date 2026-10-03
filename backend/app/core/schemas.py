from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from app.core.enums import AmbulanceStatus, AccidentStatus, Severity

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Location(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class Ambulance(BaseModel):
    ambulance_id: str
    base_name: str
    location: Location
    status: AmbulanceStatus = AmbulanceStatus.AVAILABLE

class Weather(BaseModel):
    temperature_c: Optional[float] = None
    precipitation_mm: Optional[float] = None
    visibility_m: Optional[float] = None
    wind_kph: Optional[float] = None
    weather_code: Optional[int] = None
    summary: Optional[str] = None


class AccidentReport(BaseModel):
    """What a person, a camera or the simulator sends when reporting an accident."""
    location: Location
    severity: Severity
    description: Optional[str] = None
    source: str = "manual"                         # manual | camera | simulation
    camera_id: Optional[str] = None
    detection_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    severity_confidence: Optional[float] = Field(default=None, ge=0, le=1)
    frame_path: Optional[str] = None
    vehicle_count: Optional[int] = None
    detected_at: Optional[datetime] = None


class Accident(AccidentReport):
    """A stored accident: the report plus what the system adds."""
    accident_id: str
    status: AccidentStatus = AccidentStatus.AWAITING_AMBULANCE
    assigned_ambulance_id: Optional[str] = None
    reported_at: datetime = Field(default_factory=utc_now)
    weather: Optional[Weather] = None
    road_type: Optional[str] = None
