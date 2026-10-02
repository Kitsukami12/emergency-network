import heapq
import math

from app.services.routing import get_graph

_MAX_SPEED = None

def _max_speed():
    global _MAX_SPEED
    if _MAX_SPEED is None:
        _MAX_SPEED = max(d["speed_kph"] for _, _, d in get_graph().edges(data=True)) / 3.6
    return _MAX_SPEED

def haversine_m(lat1, lon1, lat2, lon2):
    """Straight-line distance in meters between two points."""
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def astar(start: int, goal: int):
    """Return (travel_time_seconds, [node ids]) or None if no route."""
    G = get_graph()
    max_speed = _max_speed()
    gy, gx = G.nodes[goal]["y"], G.nodes[goal]["x"]

    def h(n):
        # TODO 1: straight-line meters from node n to the goal, divided by max_speed
        #         (this is the heuristic for A* search)
        ny, nlon = G.nodes[n]["y"], G.nodes[n]["x"]
        return haversine_m(ny, nlon, gy, gx) / max_speed

    best = {start: 0.0}          # cheapest known time to reach each node
    came_from = {}
    queue = [(h(start), start)]  # (f score, node)

    while queue:
        f, node = heapq.heappop(queue)
        if node == goal:
            path = [node]
            while node in came_from:
                node = came_from[node]
                path.append(node)
            path.reverse()
            return best[goal], path
            ...
        for nbr in G.successors(node):
            # a graph can have several roads between two junctions: take the fastest
            edge_time = min(d["travel_time"] for d in G[node][nbr].values())
            new_g = best[node] + edge_time
            # TODO 3: if nbr is unseen OR new_g < best[nbr]:
            #         record best[nbr], came_from[nbr] = node,
            #         and push (new_g + h(nbr), nbr) onto the queue
            if nbr not in best or new_g < best[nbr]:
                best[nbr] = new_g
                came_from[nbr] = node
                heapq.heappush(queue, (new_g + h(nbr), nbr))

    return None