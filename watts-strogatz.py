#!/usr/bin/python3

import matplotlib.pyplot as plt
from operator import itemgetter
import networkx as nx
from sys import exit
import random as rand
from random import random

# Number of nodes |V|, mean degree c, parameter β
# Required:
# - Number of nodes (must be > 1)
# - Mean degree (must be >= 2 and even)
# NOTE: Ring lattices must have at least degree 2
# - Parameter beta (between 0 and 1)

# TODO: Figure out the correct way to take the parameters.
# For now, just use stdin.

num_nodes: int = int(input("Number of Nodes: "))
if num_nodes < 1:
    print("Number of nodes must be positive")
    exit(1)

mean_degree: int = int(input("Mean Degree: "))
if mean_degree < 2 or mean_degree % 2 != 0:
    print("mean_degree must be even and >= 2")
    exit(3)

beta: float = float(input("Parameter Beta: "))
if beta < 0 or beta > 1:
    print("beta must be between 0 and 1 (inclusive on both ends)")
    exit(2)

#  G = A regular ring lattice with |V| nodes and degree c
# Generates a ring with `num_nodes` nodes
g = nx.cycle_graph(num_nodes)

# Add extra links only if we need to
if mean_degree > 2:
    distance_per_dir: int = mean_degree // 2
    for node in g.nodes():
        # Every node only needs to "look forward" for the missing connections,
        # b/c all backwards connections have been handled already
        g.add_edges_from(
            [
                (node, (node + dist) % num_nodes)
                for dist in range(2, distance_per_dir + 1)
            ]
        )

result = nx.Graph()

#  for node vi (starting from v1), and all edges e(vi , vj), i < j do
for node in g.nodes():
    for neighbor in g.neighbors(node):
        if neighbor <= node:
            result.add_edge(node, neighbor)
            continue

        # vk = Select a node from V uniformly at random.
        rand_node = rand.choice(list(g.nodes()))

        # if rewiring e(vi , vj) to e(vi , vk) does not create loops in the graph or multiple edges between vi and vk then
        if rand_node == node or rand_node in g.neighbors(node):
            result.add_edge(node, neighbor)
            continue

        # rewire e(vi , vj) with probability β: E = E−{e(vi , vj)}, E = E∪{e(vi , vk)};
        if random() > beta:
            result.add_edge(node, neighbor)
        else:
            result.add_edge(node, rand_node)

#  Return G(V, E)

# Avg Path length
print(nx.algorithms.shortest_paths.average_shortest_path_length(result))

# Clustering coeff
print(nx.algorithms.cluster.average_clustering(result))

# Visualize the result
nx.draw(result)
plt.savefig("watts-strogatz.png")
