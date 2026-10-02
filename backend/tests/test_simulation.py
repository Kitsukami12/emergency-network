from app.core.config import AMBULANCE_SEED
from app.core.seeds import load_ambulances
from app.services.assignment import assign_nearest
from app.simulation.engine import make_scenario, simulate


def test_second_accident_waits_when_one_ambulance():
    ambulances = load_ambulances(AMBULANCE_SEED)[:1]
    incidents = make_scenario(0, 2, 1)       # 2 accidents, both arrive within 1 second
    records, unserved = simulate(assign_nearest, ambulances, incidents)
    assert len(records) == 2
    assert unserved == 0
    assert max(r["wait_min"] for r in records) > 0