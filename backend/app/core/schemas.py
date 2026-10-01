from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from app.core.enums import AccidentStatus, AmbulanceStatus, Severity


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


class AccidentReport(BaseModel):
    """What a person (or the simulator) sends when reporting an accident."""
    location: Location
    severity: Severity
    description: Optional[str] = None


class Accident(AccidentReport):
    """A stored accident: the report plus what the system adds."""
    accident_id: str
    status: AccidentStatus = AccidentStatus.AWAITING_AMBULANCE
    assigned_ambulance_id: Optional[str] = None
    reported_at: datetime = Field(default_factory=utc_now)