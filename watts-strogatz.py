#!/usr/bin/python3

from __future__ import annotations

import matplotlib.pyplot as plt
from operator import itemgetter
import networkx as nx
from sys import exit
from random import choice, random
from time import time_ns, sleep

import multiprocessing as mp
from multiprocessing import Process

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

start = time_ns()


def print_timing(section: str):
    global start
    print(f"{section:25}", (time_ns() - start) / 1000000, "ms")
    start = time_ns()


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

print_timing("Ring lattice")

result = nx.Graph()

#  for node vi (starting from v1), and all edges e(vi , vj), i < j do
for node in g.nodes():
    for neighbor in g.neighbors(node):
        if neighbor <= node:
            result.add_edge(node, neighbor)
            continue

        # vk = Select a node from V uniformly at random.
        rand_node = choice(list(g))

        # if rewiring e(vi , vj) to e(vi , vk) does not create loops in the graph or multiple edges between vi and vk then
        if rand_node == node or rand_node in g.neighbors(node):
            result.add_edge(node, neighbor)
            continue

        # rewire e(vi , vj) with probability β: E = E−{e(vi , vj)}, E = E∪{e(vi , vk)};
        if random() > beta:
            result.add_edge(node, neighbor)
        else:
            result.add_edge(node, rand_node)

print_timing("Randomize edges")
#  Return G(V, E)


def compute_metrics(
    G,
    q: "mp.Queue[tuple[int, float]]",
    x_endpoints: tuple[int, int],
    y_endpoints: tuple[int, int],
):
    shortest_path = 0
    clustering = 0
    nodes = list(G)
    for node in nodes[x_endpoints[0] : x_endpoints[1]]:
        # for the shortest paths, we only need to add the forward facing paths
        if node % 1000:
            print("Processing", node)

        shortest_path += sum(
            nx.shortest_path_length(G, node, dest)
            for dest in nodes[y_endpoints[0] : y_endpoints[1]]
            if dest > node
        )

    q.put((shortest_path, clustering))


process_count = mp.cpu_count() // 2

print("CPUs found", process_count)

items_per_process = result.number_of_nodes() // process_count

print("Items per process", items_per_process)

results_queue: "mp.Queue[tuple[int,float]]" = mp.Queue()
# Children take only a specific square
children = [
    Process(
        target=compute_metrics,
        args=(
            result,
            results_queue,
            (x_start, x_start + items_per_process - 1),
            (y_start, y_start + items_per_process - 1),
        ),
    )
    for x_start in range(0, result.number_of_nodes(), items_per_process)
    for y_start in range(0, result.number_of_nodes(), items_per_process)
    if x_start <= y_start
]

for child in children:
    child.start()

print(f"Spawned {len(children)} subprocesses")


shortest_path = 0
clustering = 0.0

while len(children) != 0:
    # wait until at least 1 process is done
    while all(proc.is_alive() for proc in children):
        sleep(5)

    # take from the queue
    while not results_queue.empty():
        shortest_path_temp, clustering_temp = results_queue.get()
        shortest_path += shortest_path_temp
        clustering += clustering_temp

    # remove done children
    children = [child for child in children if child.is_alive()]

    print(f"{len(children)} children remaining")

print("Average Shortest Path Length", shortest_path / result.size())

print("Average Clustering", clustering / result.size())

# Avg Path length
# print(nx.algorithms.shortest_paths.average_shortest_path_length(result))

# Clustering coeff
# print(nx.algorithms.cluster.average_clustering(result))

print_timing("Metrics")

# TODO: Make flag?
# Visualize the result
# nx.draw(result)
# plt.savefig("watts-strogatz.png")

print_timing("Visualization")
