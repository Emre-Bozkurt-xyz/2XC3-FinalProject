import csv
import math
import time

from final_project_part1 import DirectedWeightedGraph
from final_project_part2 import a_star
from min_heap import MinHeap, Element

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def load_london_stations(stations_csv):
    stations = {}
    with open(stations_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            station_id = int(row["id"])
            stations[station_id] = {
                "name": row["name"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
            }
    return stations


def load_london_connections(connections_csv):
    connections = []
    with open(connections_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            connections.append({
                "station1": int(row["station1"]),
                "station2": int(row["station2"]),
                "line": row["line"],
            })
    return connections


def build_london_graph(stations, connections):
    G = DirectedWeightedGraph()

    for station_id in stations:
        G.add_node(station_id)

    edge_lines = {}

    for conn in connections:
        u = conn["station1"]
        v = conn["station2"]
        line = conn["line"]

        lat1 = stations[u]["latitude"]
        lon1 = stations[u]["longitude"]
        lat2 = stations[v]["latitude"]
        lon2 = stations[v]["longitude"]

        weight = haversine_km(lat1, lon1, lat2, lon2)

        G.add_edge(u, v, weight)
        G.add_edge(v, u, weight)

        if (u, v) not in edge_lines:
            edge_lines[(u, v)] = set()
        if (v, u) not in edge_lines:
            edge_lines[(v, u)] = set()

        edge_lines[(u, v)].add(line)
        edge_lines[(v, u)].add(line)

    return G, edge_lines


def build_heuristic(stations, destination):
    h = {}
    dest_lat = stations[destination]["latitude"]
    dest_lon = stations[destination]["longitude"]

    for station_id, info in stations.items():
        h[station_id] = haversine_km(
            info["latitude"], info["longitude"],
            dest_lat, dest_lon
        )

    return h


def reconstruct_path(pred, source, dest):
    if source == dest:
        return [source]

    if dest not in pred:
        return []

    path = []
    current = dest
    while current != source:
        path.append(current)
        current = pred.get(current)
        if current is None:
            return []
    path.append(source)
    path.reverse()
    return path


def dijkstra_with_stats(G, source, dest):
    start = time.perf_counter_ns()

    pred = {}
    dist = {}
    visited = set()
    relaxations = 0
    popped = 0

    Q = MinHeap([])
    nodes = list(G.adj.keys())

    for node in nodes:
        dist[node] = float("inf")
        Q.insert(Element(node, float("inf")))

    dist[source] = 0
    Q.decrease_key(source, 0)

    while not Q.is_empty():
        current_element = Q.extract_min()
        current = current_element.value
        popped += 1

        if current in visited:
            continue
        visited.add(current)

        if current == dest:
            break

        for neighbour in G.adj[current]:
            if neighbour in visited:
                continue

            new_dist = dist[current] + G.w(current, neighbour)
            if new_dist < dist[neighbour]:
                dist[neighbour] = new_dist
                pred[neighbour] = current
                Q.decrease_key(neighbour, new_dist)
                relaxations += 1

    end = time.perf_counter_ns()

    path = reconstruct_path(pred, source, dest)

    return {
        "pred": pred,
        "path": path,
        "distance": dist[dest],
        "runtime_ns": end - start,
        "visited_count": len(visited),
        "popped_count": popped,
        "relaxations": relaxations,
    }


def a_star_with_stats(G, source, dest, h):
    start = time.perf_counter_ns()

    pred = {}
    dist = {}
    g_score = {}
    visited = set()
    relaxations = 0
    popped = 0

    Q = MinHeap([])
    nodes = list(G.adj.keys())

    for node in nodes:
        Q.insert(Element(node, float("inf")))
        dist[node] = float("inf")
        g_score[node] = float("inf")
        pred[node] = None

    g_score[source] = 0
    Q.decrease_key(source, h[source])

    while not Q.is_empty():
        current_element = Q.extract_min()
        current = current_element.value
        popped += 1

        if current in visited:
            continue
        visited.add(current)

        dist[current] = g_score[current]

        if current == dest:
            break

        for neighbour in G.adj[current]:
            if neighbour in visited:
                continue

            tentative_g = g_score[current] + G.w(current, neighbour)

            if tentative_g < g_score[neighbour]:
                g_score[neighbour] = tentative_g
                pred[neighbour] = current
                Q.decrease_key(neighbour, tentative_g + h[neighbour])
                relaxations += 1

    end = time.perf_counter_ns()

    path = reconstruct_path(pred, source, dest)

    return {
        "pred": pred,
        "path": path,
        "distance": g_score[dest],
        "runtime_ns": end - start,
        "visited_count": len(visited),
        "popped_count": popped,
        "relaxations": relaxations,
    }


def get_path_lines(path, edge_lines):
    path_lines = []
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        lines = edge_lines.get((u, v), set())
        path_lines.append(lines)
    return path_lines


def count_transfers(path, edge_lines):
    if len(path) < 2:
        return 0

    edge_line_sets = get_path_lines(path, edge_lines)

    current_possible = set(edge_line_sets[0])
    transfers = 0

    for next_lines in edge_line_sets[1:]:
        overlap = current_possible.intersection(next_lines)
        if overlap:
            current_possible = overlap
        else:
            transfers += 1
            current_possible = set(next_lines)

    return transfers


def count_lines_used(path, edge_lines):
    used = set()
    for lines in get_path_lines(path, edge_lines):
        used.update(lines)
    return len(used)


def is_same_line_path(path, edge_lines):
    if len(path) < 2:
        return True

    edge_line_sets = get_path_lines(path, edge_lines)
    common = set(edge_line_sets[0])

    for lines in edge_line_sets[1:]:
        common = common.intersection(lines)
        if not common:
            return False

    return True


def compare_pair(G, stations, edge_lines, source, dest):
    h = build_heuristic(stations, dest)

    dijkstra_result = dijkstra_with_stats(G, source, dest)
    a_star_result = a_star_with_stats(G, source, dest, h)

    path = dijkstra_result["path"]  # should match A* path cost-wise

    return {
        "source": source,
        "dest": dest,
        "source_name": stations[source]["name"],
        "dest_name": stations[dest]["name"],

        "dijkstra_runtime_ns": dijkstra_result["runtime_ns"],
        "astar_runtime_ns": a_star_result["runtime_ns"],

        "dijkstra_visited": dijkstra_result["visited_count"],
        "astar_visited": a_star_result["visited_count"],

        "dijkstra_popped": dijkstra_result["popped_count"],
        "astar_popped": a_star_result["popped_count"],

        "dijkstra_relaxations": dijkstra_result["relaxations"],
        "astar_relaxations": a_star_result["relaxations"],

        "distance": dijkstra_result["distance"],
        "path_edges": max(0, len(path) - 1),
        "transfers": count_transfers(path, edge_lines),
        "lines_used": count_lines_used(path, edge_lines),
        "same_line": is_same_line_path(path, edge_lines),
    }


def run_all_pairs_experiment(G, stations, edge_lines):
    results = []
    station_ids = list(stations.keys())

    for source in station_ids:
        for dest in station_ids:
            if source == dest:
                continue
            results.append(compare_pair(G, stations, edge_lines, source, dest))

    return results