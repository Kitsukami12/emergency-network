"""
Downloads the Indore road network once and saves it to disk.
Run from the project root:  python scripts/build_graph.py
"""
import time
from pathlib import Path

import osmnx as ox

# ---- Settings (change these if needed) ----
CENTER = (22.7196, 75.8577)   # central Indore (lat, lon)
RADIUS_M = 10000              # 10 km around the center
OUT_FILE = Path("data/graph/indore.graphml")


def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print("1/5 Downloading roads from OpenStreetMap (can take 1-5 min)...")
    t = time.time()
    G = ox.graph_from_point(CENTER, dist=RADIUS_M, network_type="drive")
    print(f"    done in {time.time() - t:.0f}s")
    print(f"    raw graph: {len(G.nodes)} nodes, {len(G.edges)} edges")

    print("2/5 Keeping only the fully connected part of the map...")
    G = ox.truncate.largest_component(G, strongly=True)
    print(f"    connected graph: {len(G.nodes)} nodes, {len(G.edges)} edges")

    print("3/5 Adding speeds and travel times to every road...")
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    print("4/5 Saving to disk...")
    ox.save_graphml(G, OUT_FILE)
    size_mb = OUT_FILE.stat().st_size / 1_000_000
    print(f"    saved {OUT_FILE} ({size_mb:.1f} MB)")

    print("5/5 Checking the file reloads properly...")
    t = time.time()
    G2 = ox.load_graphml(OUT_FILE)
    print(f"    reloaded in {time.time() - t:.1f}s: "
          f"{len(G2.nodes)} nodes, {len(G2.edges)} edges")

    # Sample one road to confirm the data we need is present
    u, v, data = next(iter(G2.edges(data=True)))
    print("    sample road:", {k: data.get(k) for k in
                              ("length", "speed_kph", "travel_time")})

    print("\nAll good. Optional: opening a preview picture...")
    ox.plot_graph(G2, node_size=0, edge_linewidth=0.3)


if __name__ == "__main__":
    main()