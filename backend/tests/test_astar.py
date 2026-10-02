import random
import networkx as nx
from app.services.astar import astar
from app.services.routing import get_graph


def test_matches_networkx_on_random_pairs():
    G = get_graph()
    nodes = list(G.nodes)
    rng = random.Random(42)
    for _ in range(30):
        a, b = rng.sample(nodes, 2)
        mine, _ = astar(a, b)
        theirs = nx.shortest_path_length(G, a, b, weight="travel_time")
        assert abs(mine - theirs) < 1e-6