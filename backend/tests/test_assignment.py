from app.core.schemas import Accident, Ambulance, Location
from app.services import assignment


def _amb(aid):
    return Ambulance(ambulance_id=aid, base_name=aid, location=Location(lat=22.7, lon=75.8))


def _acc(aid, severity):
    return Accident(accident_id=aid, location=Location(lat=22.7, lon=75.8), severity=severity)


def test_nearest_is_greedy(monkeypatch):
    # rows = ambulances A, B; columns = accidents 1, 2 (seconds)
    monkeypatch.setattr(assignment, "travel_time_matrix",
                        lambda ambs, accs: [[4, 5], [6, 20]])
    ambs = [_amb("A"), _amb("B")]
    accs = [_acc("ACC-1", "HIGH"), _acc("ACC-2", "LOW")]
    result = assignment.assign_nearest(ambs, accs)
    assert result == {"ACC-1": "A", "ACC-2": "B"}


def test_ambulance_not_used_twice(monkeypatch):
    # 1 ambulance, 2 accidents: only the more severe one gets it
    monkeypatch.setattr(assignment, "travel_time_matrix",
                        lambda ambs, accs: [[4, 5]])
    result = assignment.assign_nearest([_amb("A")],
                                       [_acc("ACC-1", "LOW"), _acc("ACC-2", "HIGH")])
    assert result == {"ACC-2": "A"}

def test_hungarian_beats_greedy(monkeypatch):
    # same 4/5/6/20 example, equal severity so weights don't change the answer
    monkeypatch.setattr(assignment, "travel_time_matrix",
                        lambda ambs, accs: [[4, 5], [6, 20]])
    ambs = [_amb("A"), _amb("B")]
    accs = [_acc("ACC-1", "HIGH"), _acc("ACC-2", "HIGH")]
    result = assignment.assign_hungarian(ambs, accs)
    assert result == {"ACC-1": "B", "ACC-2": "A"}   # total 11, Nearest gives 24


def test_hungarian_fewer_ambulances(monkeypatch):
    # 1 ambulance, 2 accidents: the heavier-weighted (HIGH) one should get it
    monkeypatch.setattr(assignment, "travel_time_matrix",
                        lambda ambs, accs: [[4, 5]])
    result = assignment.assign_hungarian([_amb("A")],
                                         [_acc("ACC-1", "LOW"), _acc("ACC-2", "HIGH")])
    assert result == {"ACC-2": "A"}


def test_hungarian_beats_greedy(monkeypatch):
    monkeypatch.setattr(assignment, "travel_time_matrix",
                        lambda ambs, accs: [[4, 5], [6, 20]])
    accs = [_acc("ACC-1", "HIGH"), _acc("ACC-2", "HIGH")]
    result = assignment.assign_hungarian([_amb("A"), _amb("B")], accs)
    assert result == {"ACC-1": "B", "ACC-2": "A"}   # total 11, Nearest gives 24


def test_hungarian_scarce_serves_severe(monkeypatch):
    monkeypatch.setattr(assignment, "travel_time_matrix",
                        lambda ambs, accs: [[4, 5]])
    result = assignment.assign_hungarian([_amb("A")],
                                         [_acc("ACC-1", "LOW"), _acc("ACC-2", "HIGH")])
    assert result == {"ACC-2": "A"}