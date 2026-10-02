import argparse
import statistics

from app.core.config import AMBULANCE_SEED
from app.core.seeds import load_ambulances
from app.services.assignment import assign_hungarian, assign_nearest
from app.simulation.engine import make_scenario, simulate, summarize

p = argparse.ArgumentParser()
p.add_argument("--accidents", type=int, default=20)
p.add_argument("--ambulances", type=int, default=12)
p.add_argument("--minutes", type=int, default=30)
p.add_argument("--seeds", type=int, default=20)
args = p.parse_args()

ambulances = load_ambulances(AMBULANCE_SEED)[:args.ambulances]
out = {"nearest": [], "hungarian": []}
for seed in range(args.seeds):
    incidents = make_scenario(seed, args.accidents, args.minutes * 60)
    for name, fn in [("nearest", assign_nearest), ("hungarian", assign_hungarian)]:
        out[name].append(summarize(*simulate(fn, ambulances, incidents)))

print(f"{args.accidents} accidents in {args.minutes} min, "
      f"{len(ambulances)} ambulances, {args.seeds} seeds\n")
print(f"{'metric':<10}{'nearest':>18}{'hungarian':>18}")
for m in ["mean", "median", "p90", "max", "wait", "weighted", "unserved"]:
    row = f"{m:<10}"
    for name in out:
        v = [r[m] for r in out[name]]
        row += f"{statistics.mean(v):>10.2f} ±{statistics.stdev(v):>5.2f}"
    print(row)