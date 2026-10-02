from app.core import db
from app.core.config import AMBULANCE_SEED
from app.core.enums import AccidentStatus, AmbulanceStatus
from app.core.schemas import AccidentReport, Location
from app.core.seeds import load_ambulances
from app.services.dispatch import dispatch_pending


def test_dispatch_updates_database(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "DB_FILE", tmp_path / "t.db")
    db.init_db()
    db.seed_ambulances(load_ambulances(AMBULANCE_SEED))
    acc = db.add_accident(AccidentReport(
        location=Location(lat=22.72, lon=75.86), severity="HIGH"))

    out = dispatch_pending("hungarian")

    assert len(out) == 1
    amb_id = out[0]["ambulance_id"]
    stored = db.get_accident(acc.accident_id)
    assert stored.status == AccidentStatus.AMBULANCE_ASSIGNED
    assert stored.assigned_ambulance_id == amb_id
    amb = next(a for a in db.list_ambulances() if a.ambulance_id == amb_id)
    assert amb.status == AmbulanceStatus.DISPATCHED