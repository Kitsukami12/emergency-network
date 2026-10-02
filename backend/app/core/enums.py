from enum import Enum


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AccidentStatus(str, Enum):
    DETECTED = "DETECTED"
    ASSESSING = "ASSESSING"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"   # low-confidence detection, human checks
    AWAITING_AMBULANCE = "AWAITING_AMBULANCE"
    AMBULANCE_ASSIGNED = "AMBULANCE_ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    ARRIVED = "ARRIVED"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class AmbulanceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DISPATCHED = "DISPATCHED"       # assigned, heading to the accident
    AT_SCENE = "AT_SCENE"
    TRANSPORTING = "TRANSPORTING"
    AT_HOSPITAL = "AT_HOSPITAL"
    RETURNING = "RETURNING"         # heading back to base
    OFFLINE = "OFFLINE"