import sqlite3
import uuid
import json

from contextlib import contextmanager

from app.core.config import DB_FILE
from app.core.schemas import Accident, AccidentReport, Ambulance, Location
from app.core.enums import AccidentStatus
from app.core.transitions import can_transition
from app.core.enums import AccidentStatus, AmbulanceStatus
from app.core.schemas import Weather

SCHEMA = """
CREATE TABLE IF NOT EXISTS ambulances (
    ambulance_id TEXT PRIMARY KEY,
    base_name    TEXT NOT NULL,
    lat          REAL NOT NULL,
    lon          REAL NOT NULL,
    status       TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS accidents (
    accident_id           TEXT PRIMARY KEY,
    lat                   REAL NOT NULL,
    lon                   REAL NOT NULL,
    severity              TEXT NOT NULL,
    description           TEXT,
    status                TEXT NOT NULL,
    assigned_ambulance_id TEXT,
    reported_at           TEXT NOT NULL,
    source                TEXT NOT NULL DEFAULT 'manual',
    camera_id             TEXT,
    detection_confidence  REAL,
    severity_confidence   REAL,
    frame_path            TEXT,
    vehicle_count         INTEGER,
    detected_at           TEXT,
    weather_json          TEXT,
    road_type             TEXT
);
"""


@contextmanager
def connect():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def seed_ambulances(ambulances: list[Ambulance]) -> None:
    """Insert ambulances. Safe to run twice: existing IDs are skipped."""
    with connect() as conn:
        for a in ambulances:
            conn.execute(
                "INSERT OR IGNORE INTO ambulances VALUES (?, ?, ?, ?, ?)",
                (a.ambulance_id, a.base_name, a.location.lat,
                 a.location.lon, a.status.value),
            )


def list_ambulances() -> list[Ambulance]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM ambulances ORDER BY ambulance_id"
        ).fetchall()
    return [
        Ambulance(
            ambulance_id=r["ambulance_id"],
            base_name=r["base_name"],
            location=Location(lat=r["lat"], lon=r["lon"]),
            status=r["status"],
        )
        for r in rows
    ]


def add_accident(report: AccidentReport, weather: Weather | None = None,
                 road_type: str | None = None) -> Accident:
    accident = Accident(
        accident_id="ACC-" + uuid.uuid4().hex[:8],
        weather=weather,
        road_type=road_type,
        **report.model_dump(),
    )
    with connect() as conn:
        conn.execute(
            """INSERT INTO accidents (accident_id, lat, lon, severity, description, status,
                   assigned_ambulance_id, reported_at, source, camera_id, detection_confidence,
                   severity_confidence, frame_path, vehicle_count, detected_at,
                   weather_json, road_type)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (accident.accident_id, accident.location.lat, accident.location.lon,
             accident.severity.value, accident.description, accident.status.value,
             accident.assigned_ambulance_id, accident.reported_at.isoformat(),
             accident.source, accident.camera_id, accident.detection_confidence,
             accident.severity_confidence, accident.frame_path, accident.vehicle_count,
             accident.detected_at.isoformat() if accident.detected_at else None,
             weather.model_dump_json() if weather else None, road_type),
        )
    return accident


def get_accident(accident_id: str) -> Accident | None:
    with connect() as conn:
        r = conn.execute(
            "SELECT * FROM accidents WHERE accident_id = ?", (accident_id,)
        ).fetchone()
    if r is None:
        return None
    return Accident(
        accident_id=r["accident_id"],
        location=Location(lat=r["lat"], lon=r["lon"]),
        severity=r["severity"],
        description=r["description"],
        status=r["status"],
        assigned_ambulance_id=r["assigned_ambulance_id"],
        reported_at=r["reported_at"],
        source=r["source"],
        camera_id=r["camera_id"],
        detection_confidence=r["detection_confidence"],
        severity_confidence=r["severity_confidence"],
        frame_path=r["frame_path"],
        vehicle_count=r["vehicle_count"],
        detected_at=r["detected_at"],
        weather=Weather.model_validate_json(r["weather_json"]) if r["weather_json"] else None,
        road_type=r["road_type"],
    )


class IllegalTransition(Exception):
    pass


def change_status(accident_id: str, new_status: AccidentStatus) -> Accident:
    accident = get_accident(accident_id)
    if accident is None:
        raise LookupError(f"Accident {accident_id} not found")
    if not can_transition(accident.status, new_status):
        raise IllegalTransition(
            f"{accident.status.value} -> {new_status.value} is not allowed"
        )
    with connect() as conn:
        conn.execute(
            "UPDATE accidents SET status = ? WHERE accident_id = ?",
            (new_status.value, accident_id),
        )
    return get_accident(accident_id)

def list_accidents() -> list[Accident]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT accident_id FROM accidents ORDER BY reported_at DESC"
        ).fetchall()
    return [get_accident(r["accident_id"]) for r in rows]

def list_accidents_by_status(status: AccidentStatus) -> list[Accident]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT accident_id FROM accidents WHERE status = ? ORDER BY reported_at",
            (status.value,),
        ).fetchall()
    return [get_accident(r["accident_id"]) for r in rows]


def assign_ambulance(accident_id: str, ambulance_id: str) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE accidents SET assigned_ambulance_id = ? WHERE accident_id = ?",
            (ambulance_id, accident_id),
        )


def set_ambulance_status(ambulance_id: str, status: AmbulanceStatus) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE ambulances SET status = ? WHERE ambulance_id = ?",
            (status.value, ambulance_id),
        )