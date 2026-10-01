from enum import Enum


class AmbulanceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DISPATCHED = "DISPATCHED"            # assigned, heading to the patient
    AT_SCENE = "AT_SCENE"                # reached the accident
    TRANSPORTING = "TRANSPORTING"        # carrying patient to hospital
    AT_HOSPITAL = "AT_HOSPITAL"          # patient handed over
    RETURNING = "RETURNING"              # heading back to base
    OFFLINE = "OFFLINE"                  # not in service


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AccidentStatus(str, Enum):
    AWAITING_AMBULANCE = "AWAITING_AMBULANCE"   # reported, no ambulance yet
    AMBULANCE_ASSIGNED = "AMBULANCE_ASSIGNED"
    PATIENT_PICKED_UP = "PATIENT_PICKED_UP"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"