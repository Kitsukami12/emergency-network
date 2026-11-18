import random
from types import SimpleNamespace

import pytest

from app.core.enums import AccidentStatus as S, AmbulanceStatus as A
from app.services import progress


class FakeDB:
    class IllegalTransition(Exception):
        pass

    def __init__(self, accidents, ambulances):
        self.acc = {a.accident_id: a for a in accidents}
        self.amb = {a.ambulance_id: a for a in ambulances}

    def list_accidents(self):
        return list(self.acc.values())

    def list_ambulances(self):
        return list(self.amb.values())

    def change_status(self, accident_id, new):
        self.acc[accident_id].status = new

    def set_ambulance_status(self, ambulance_id, status):
        self.amb[ambulance_id].status = status


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    monkeypatch.setattr(progress, "DEMO_SPEED", 1.0)
    progress.plans.clear()
    progress.free_at.clear()


def _world(monkeypatch, amb_status=A.AVAILABLE):
    acc = SimpleNamespace(accident_id="ACC-1", status=S.AMBULANCE_ASSIGNED, assigned_ambulance_id="A1")
    amb = SimpleNamespace(ambulance_id="A1", status=amb_status)
    db = FakeDB([acc], [amb])
    monkeypatch.setattr(progress, "db", db)
    return acc, amb


def test_done_time_is_within_two_minutes_of_eta():
    for seed in range(200):
        plan = progress.make_plan("A1", 7.0, 0.0, random.Random(seed))
        assert 5 * 60 <= plan["done_at"] <= 9 * 60
        assert plan["arrive_at"] < plan["done_at"] < plan["free_at"]


def test_incident_walks_through_every_status_then_ambulance_returns(monkeypatch):
    acc, amb = _world(monkeypatch)
    progress.plans["ACC-1"] = {"ambulance_id": "A1", "move_at": 10, "arrive_at": 100,
                               "done_at": 160, "free_at": 400}
    progress.tick(now=5)
    assert acc.status == S.AMBULANCE_ASSIGNED
    progress.tick(now=20)
    assert acc.status == S.EN_ROUTE
    progress.tick(now=120)
    assert acc.status == S.ARRIVED and amb.status == A.AT_SCENE
    progress.tick(now=200)
    assert acc.status == S.RESOLVED
    assert amb.status != A.AVAILABLE            # still driving back
    progress.tick(now=399)
    assert amb.status != A.AVAILABLE
    progress.tick(now=401)
    assert amb.status == A.AVAILABLE


def test_a_late_tick_still_moves_one_legal_step_at_a_time(monkeypatch):
    acc, amb = _world(monkeypatch)
    seen = []
    orig = progress.db.change_status
    progress.db.change_status = lambda i, s: (seen.append(s), orig(i, s))
    progress.plans["ACC-1"] = {"ambulance_id": "A1", "move_at": 1, "arrive_at": 2,
                               "done_at": 3, "free_at": 4}
    progress.tick(now=1000)
    assert seen == [S.EN_ROUTE, S.ARRIVED, S.RESOLVED]


def test_unplanned_incident_gets_a_default_plan(monkeypatch):
    acc, amb = _world(monkeypatch)
    progress.tick(now=0)
    assert "ACC-1" in progress.plans


def test_busy_ambulance_with_no_incident_is_released(monkeypatch):
    acc, amb = _world(monkeypatch, amb_status=A.AT_SCENE)
    acc.status = S.RESOLVED
    progress.tick(now=0)
    assert amb.status == A.AT_SCENE
    progress.tick(now=10 * 60)
    assert amb.status == A.AVAILABLE
