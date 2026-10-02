import random
import statistics
from datetime import datetime, timedelta, timezone

from app.core.config import AMBULANCE_SEED
from app.core.schemas import Accident, Location
from app.core.seeds import load_ambulances
from app.services.assignment import (
    assign_hungarian, assign_nearest, travel_time_matrix)
from app.services.routing import get_graph

SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
SEV_PROBS = [0.4, 0.3, 0.2, 0.1]   # assumption: minor accidents are most common
N_ACCIDENTS = 6
N_SEEDS = 20


def make_scenario(seed, nodes, G):
    rng = random.Random(seed)
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    accidents = []
    for k in range(N_ACCIDENTS):
        n = rng.choice(nodes)
        accidents.append(Accident(
            accident_id=f"S{seed}-{k}",
            location=Location(lat=G.nodes[n]["y"], lon=G.nodes[n]["x"]),
            severity=rng.choices(SEVERITIES, SEV_PROBS)[0],
            reported_at=t0 + timedelta(seconds=k),
        ))
    return accidents


def evaluate(assignment, ambulances, accidents):
    """Response times (minutes) for served accidents, and count of unserved."""
    matrix = travel_time_matrix(ambulances, accidents)
    amb_index = {a.ambulance_id: i for i, a in enumerate(ambulances)}
    times = []
    for j, acc in enumerate(accidents):
        if acc.accident_id in assignment:
            i = amb_index[assignment[acc.accident_id]]
            times.append(matrix[i][j] / 60)
    return times, len(accidents) - len(times)


def main():
    G = get_graph()
    nodes = list(G.nodes)
    ambulances = load_ambulances(AMBULANCE_SEED)
    results = {"nearest": [], "hungarian": []}

    for seed in range(N_SEEDS):
        accidents = make_scenario(seed, nodes, G)
        for name, fn in [("nearest", assign_nearest), ("hungarian", assign_hungarian)]:
            times, unserved = evaluate(fn(ambulances, accidents), ambulances, accidents)
            results[name].append({
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "max": max(times),
                "total": sum(times),
                "unserved": unserved,
            })

    print(f"{N_ACCIDENTS} accidents, {len(ambulances)} ambulances, {N_SEEDS} seeds\n")
    print(f"{'metric':<10}{'nearest':>18}{'hungarian':>18}")
    for metric in ["mean", "median", "max", "total", "unserved"]:
        row = f"{metric:<10}"
        for name in ["nearest", "hungarian"]:
            vals = [r[metric] for r in results[name]]
            row += f"{statistics.mean(vals):>10.2f} ±{statistics.stdev(vals):>5.2f}"
        print(row)

    wins = sum(h["total"] < n["total"] - 1e-9
               for n, h in zip(results["nearest"], results["hungarian"]))
    ties = sum(abs(h["total"] - n["total"]) < 1e-9
               for n, h in zip(results["nearest"], results["hungarian"]))
    print(f"\nHungarian had lower total time in {wins}/{N_SEEDS} seeds, tied in {ties}.")


if __name__ == "__main__":
    main()