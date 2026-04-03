# Author : Yashasvi Seth
# This is the second part of the final project and it holds the implementation
# of A* search algorithm which is Dijkstra's algorithm with a heuristic
# function. This makes our algorithm faster by ommitting the nodes which are
# not likely to be on the path from source to destination.

from min_heap import MinHeap, Element


def a_star(G, s, d, h):
    # h is a dictionary mapping each node to its heuristic estimate.
    # Return a tuple: (predecessor dictionary, shortest path from s to d).
    pred = {}
    dist = {}
    g_score = {}

    Q = MinHeap([])
    nodes = list(G.adj.keys())

    # Initialize
    for node in nodes:
        Q.insert(Element(node, float("inf")))
        dist[node] = float("inf")
        g_score[node] = float("inf")
        pred[node] = None

    # Source setup
    g_score[s] = 0
    Q.decrease_key(s, h[s])   # FIX: dictionary, not function

    # A* search
    while not Q.is_empty():
        current_element = Q.extract_min()
        current_node = current_element.value

        # Skip stale nodes
        if dist[current_node] != float("inf"):
            continue

        dist[current_node] = g_score[current_node]

        # Stop when destination reached
        if current_node == d:
            break

        for neighbour in G.adj[current_node]:
            if dist[neighbour] != float("inf"):
                continue

            tentative_g = g_score[current_node] + G.w(current_node, neighbour)

            if tentative_g < g_score[neighbour]:
                g_score[neighbour] = tentative_g
                pred[neighbour] = current_node

                # f = g + h
                Q.decrease_key(neighbour, tentative_g + h[neighbour])

    # Reconstruct shortest path from s to d
    path = []
    node = d

    if pred[node] is None and node != s:
        return pred, []   # unreachable

    while node is not None:
        path.append(node)
        node = pred[node]

    path.reverse()

    return pred, path