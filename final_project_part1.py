import min_heap
import random

class DirectedWeightedGraph:

    def __init__(self):
        self.adj = {}
        self.weights = {}

    def are_connected(self, node1, node2):
        for neighbour in self.adj[node1]:
            if neighbour == node2:
                return True
        return False

    def adjacent_nodes(self, node):
        return self.adj[node]

    def add_node(self, node):
        self.adj[node] = []

    def add_edge(self, node1, node2, weight):
        if node2 not in self.adj[node1]:
            self.adj[node1].append(node2)
        self.weights[(node1, node2)] = weight

    def w(self, node1, node2):
        if self.are_connected(node1, node2):
            return self.weights[(node1, node2)]

    def number_of_nodes(self):
        return len(self.adj)


def dijkstra(G, source):
    pred = {} #Predecessor dictionary. Isn't returned, but here for your understanding
    dist = {} #Distance dictionary
    Q = min_heap.MinHeap([])
    nodes = list(G.adj.keys())

    #Initialize priority queue/heap and distances
    for node in nodes:
        Q.insert(min_heap.Element(node, float("inf")))
        dist[node] = float("inf")
    Q.decrease_key(source, 0)

    #Meat of the algorithm
    while not Q.is_empty():
        current_element = Q.extract_min()
        current_node = current_element.value
        dist[current_node] = current_element.key
        for neighbour in G.adj[current_node]:
            if dist[current_node] + G.w(current_node, neighbour) < dist[neighbour]:
                Q.decrease_key(neighbour, dist[current_node] + G.w(current_node, neighbour))
                dist[neighbour] = dist[current_node] + G.w(current_node, neighbour)
                pred[neighbour] = current_node
    return dist


def bellman_ford(G, source):
    pred = {} #Predecessor dictionary. Isn't returned, but here for your understanding
    dist = {} #Distance dictionary
    nodes = list(G.adj.keys())

    #Initialize distances
    for node in nodes:
        dist[node] = float("inf")
    dist[source] = 0

    #Meat of the algorithm
    for _ in range(G.number_of_nodes()):
        for node in nodes:
            for neighbour in G.adj[node]:
                if dist[neighbour] > dist[node] + G.w(node, neighbour):
                    dist[neighbour] = dist[node] + G.w(node, neighbour)
                    pred[neighbour] = node
    return dist


def total_dist(dist):
    total = 0
    for key in dist.keys():
        total += dist[key]
    return total

def create_random_complete_graph(n,upper):
    G = DirectedWeightedGraph()
    for i in range(n):
        G.add_node(i)
    for i in range(n):
        for j in range(n):
            if i != j:
                G.add_edge(i,j,random.randint(1,upper))
    return G


#Assumes G represents its nodes as integers 0,1,...,(n-1)
def mystery(G):
    n = G.number_of_nodes()
    d = init_d(G)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][j] > d[i][k] + d[k][j]: 
                    d[i][j] = d[i][k] + d[k][j]
    return d

def init_d(G):
    n = G.number_of_nodes()
    d = [[float("inf") for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if G.are_connected(i, j):
                d[i][j] = G.w(i, j)
        d[i][i] = 0
    return d

#DIJKSTRA APPROX FUNCTION, Author: Sreyo Biswas
def dijkstra_approx(G, source, k):

    #instantiate the distance and num_relaxations dictionaries, and the priority queue
    pred = {}
    dist = {}
    num_relaxations = {}
    Q = min_heap.MinHeap([])

    for node in G.adj.keys():
        dist[node] = float("inf")
        num_relaxations[node] = 0
        #add all nodes to the priority queue with initial distance of infinity
        Q.insert(min_heap.Element(node, float("inf")))
    #decrease the key of the source node to 0, since the distance from the source to itself is 0
    dist[source] = 0
    Q.decrease_key(source, 0)

    while not Q.is_empty():
        #get the node with the smallest distance from the source
        current_element = Q.extract_min()
        current_node = current_element.value
        dist[current_node] = current_element.key
        for neighbour in G.adj[current_node]:
            #calculate the updated distance to the neighbour through the current node
            new_dist = dist[current_node] + G.w(current_node, neighbour)
            #relax if the new distance is shorter and relaxation limit has not been reached
            if new_dist < dist[neighbour] and num_relaxations[neighbour] < k:
                if neighbour in Q.map:
                    dist[neighbour] = new_dist
                    num_relaxations[neighbour] += 1
                    #update the priority queue with the new distance
                    Q.decrease_key(neighbour, new_dist)
                    pred[neighbour] = current_node
    #return distance dictionary
    return dist

#BELLMAN-FORD APPROX FUNCTION, Author: Sreyo Biswas
def bellman_ford_approx(G, source, k):
    #instantiate the distance and num_relaxations dictionaries and get the list of nodes in the graph
    pred = {}
    nodes = list(G.adj.keys())
    dist = {}
    num_relaxations = {}

    for node in G.adj.keys():
        #initialize all distances to infinity and num_relaxations to 0
        dist[node] = float("inf")
        num_relaxations[node] = 0
    dist[source] = 0

    for i in range(G.number_of_nodes()):
        for node in nodes:
            for neighbour in G.adj[node]:
                #calculate the updated distance to the neighbour through the current node
                new_dist = dist[node] + G.w(node, neighbour)
                #relax if the new distance is shorter and relaxation limit has not been reached
                if new_dist < dist[neighbour] and num_relaxations[neighbour] < k:
                    dist[neighbour] = new_dist
                    num_relaxations[neighbour] += 1
                    pred[neighbour] = node
    #return distance dictionary
    return dist

#To vary m, the following function had to be created, Author: Sreyo Biswas
def create_random_graph(n, m, max_weight):
    G = DirectedWeightedGraph()
    for i in range(n):
        G.add_node(i)
    
    edges_added = 0
    while edges_added < m:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v and not G.are_connected(u, v):
            G.add_edge(u, v, random.randint(1, max_weight))
            edges_added += 1
    return G

