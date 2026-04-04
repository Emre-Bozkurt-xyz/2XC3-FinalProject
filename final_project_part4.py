from abc import ABC, abstractmethod

from final_project_part1 import bellman_ford, dijkstra
from final_project_part2 import a_star


class Graph(ABC):
    """Base graph interface matching the UML intent."""

    def __init__(self):
        self.adj = {}

    def get_adj_nodes(self, node):
        return self.adj[node]

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = []

    @abstractmethod
    def add_edge(self, start, end, weight):
        pass

    def get_num_of_nodes(self):
        return len(self.adj)

    @abstractmethod
    def w(self, node1, node2):
        pass


class WeightedGraph(Graph):
    """Directed weighted graph implementation."""

    def __init__(self):
        super().__init__()
        self.weights = {}

    def are_connected(self, node1, node2):
        return node2 in self.adj.get(node1, [])

    def add_edge(self, start, end, weight):
        if start not in self.adj:
            self.add_node(start)
        if end not in self.adj:
            self.add_node(end)

        if end not in self.adj[start]:
            self.adj[start].append(end)
        self.weights[(start, end)] = weight

    def w(self, node1, node2):
        if self.are_connected(node1, node2):
            return self.weights[(node1, node2)]
        return float("inf")


class HeuristicGraph(WeightedGraph):
    """Weighted graph with node heuristic values for A*."""

    def __init__(self):
        super().__init__()
        self.heuristic = {}

    def set_heuristic(self, heuristic):
        self.heuristic = dict(heuristic)

    def get_heuristic(self):
        return self.heuristic


class SPAlgorithm(ABC):
    """Shortest-path algorithm interface."""

    @abstractmethod
    def calc_sp(self, graph, source, dest):
        """Return shortest-path result from source to dest."""
        pass


class Dijkstra(SPAlgorithm):
    """Adapter over existing Dijkstra implementation."""

    def calc_sp(self, graph, source, dest):
        dist = dijkstra(graph, source)
        return dist.get(dest, float("inf"))


class Bellman_Ford(SPAlgorithm):
    """Adapter over existing Bellman-Ford implementation."""

    def calc_sp(self, graph, source, dest):
        dist = bellman_ford(graph, source)
        return dist.get(dest, float("inf"))


class A_Star(SPAlgorithm):
    """Adapter over existing Part 2 A* implementation."""

    def __init__(self):
        self.last_pred = None
        self.last_path = None

    def calc_sp(self, graph, source, dest):
        if not hasattr(graph, "get_heuristic"):
            raise ValueError("A_Star requires a HeuristicGraph with heuristics set")
        heuristic = graph.get_heuristic()
        pred, path = a_star(graph, source, dest, heuristic)
        self.last_pred = pred
        self.last_path = path

        if not path:
            return float("inf")

        total_cost = 0.0
        for i in range(len(path) - 1):
            total_cost += graph.w(path[i], path[i + 1])
        return total_cost


class ShortPathFinder:
    """Coordinator that composes a graph and an algorithm."""

    def __init__(self):
        self.graph = None
        self.algorithm = None

    def set_graph(self, graph):
        self.graph = graph

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def calc_short_path(self, source, dest):
        if self.graph is None:
            raise ValueError("Graph has not been set")
        if self.algorithm is None:
            raise ValueError("Algorithm has not been set")
        return self.algorithm.calc_sp(self.graph, source, dest)
