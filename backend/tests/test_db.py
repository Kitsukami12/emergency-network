import pytest
from app.core import db
from app.core.enums import AccidentStatus as S
from app.core.schemas import AccidentReport, Location


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_FILE", tmp_path / "test.db")
    db.init_db()


def make_accident():
    return db.add_accident(
        AccidentReport(location=Location(lat=22.72, lon=75.86), severity="HIGH")
    )


def test_legal_change_works():
    acc = make_accident()
    updated = db.change_status(acc.accident_id, S.AMBULANCE_ASSIGNED)
    assert updated.status == S.AMBULANCE_ASSIGNED

def test_illegal_change_raises():
    acc = make_accident()
    with pytest.raises(db.IllegalTransition):
        db.change_status(acc.accident_id, S.RESOLVED)


def test_illegal_change_does_not_modify():
    acc = make_accident()
    with pytest.raises(db.IllegalTransition):
        db.change_status(acc.accident_id, S.RESOLVED)
    assert db.get_accident(acc.accident_id).status == S.AWAITING_AMBULANCE


def test_change_nonexistent_raises():
    with pytest.raises(LookupError):
        db.change_status("ACC-nope", S.AWAITING_AMBULANCE)

def test_full_happy_path():
    acc = make_accident()
    for step in [S.AMBULANCE_ASSIGNED, S.EN_ROUTE, S.ARRIVED, S.RESOLVED]:
        acc = db.change_status(acc.accident_id, step)
    assert acc.status == S.RESOLVED