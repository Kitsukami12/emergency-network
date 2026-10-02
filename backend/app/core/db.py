import sqlite3
import uuid
from contextlib import contextmanager

from app.core.config import DB_FILE
from app.core.schemas import Accident, AccidentReport, Ambulance, Location
from app.core.enums import AccidentStatus
from app.core.transitions import can_transition
from app.core.enums import AccidentStatus, AmbulanceStatus


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
    reported_at           TEXT NOT NULL
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


def add_accident(report: AccidentReport) -> Accident:
    accident = Accident(
        accident_id="ACC-" + uuid.uuid4().hex[:8],
        **report.model_dump(),
    )
    with connect() as conn:
        conn.execute(
            "INSERT INTO accidents VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (accident.accident_id, accident.location.lat, accident.location.lon,
             accident.severity.value, accident.description,
             accident.status.value, accident.assigned_ambulance_id,
             accident.reported_at.isoformat()),
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