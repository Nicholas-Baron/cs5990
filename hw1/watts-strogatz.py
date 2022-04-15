#!/usr/bin/python3

from __future__ import annotations

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
    print(f"{section:30}", ((time_ns() - start) // 1000000) / 1000, "s")
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

print_timing(f"Ring lattice of {num_nodes} nodes and {mean_degree} degree")

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

print_timing(f"Randomize edges (beta = {beta})")
#  Return G(V, E)


# TODO: this is overengineered b/c every process only works on 1 task. `input_q` should be replaced with the input
def compute_metrics(
    G,
    result_q: "mp.Queue[tuple[int, int, int, int]]",
    input_q: "mp.JoinableQueue[tuple[int,int]]",
):
    nodes = list(G)
    while not input_q.empty():
        x_endpoints = input_q.get()

        shortest_path = 0
        num_paths = 0
        connected_triples = 0
        triangles = 0
        for node in nodes[x_endpoints[0] : x_endpoints[1]]:
            paths = nx.shortest_path_length(G, node)
            num_paths += len(paths)
            shortest_path += sum(paths.values())

            # for clustering, we need 2 more nodes.
            # this is because clustering tries to distinguish
            # between triangles (n1, n2, n3 all connected to each other)
            # and triples (n1, n2, n3 have some direct connections between them)

            for middle in G.neighbors(node):
                # we only care about forward connections
                # because all triples/triangles will be processed according to their least element
                if middle <= node:
                    continue

                # get a third node from somewhere after middle
                for far_node in G.neighbors(middle):
                    if far_node <= middle:
                        continue

                    # at this point, we know that node connects to middle
                    # and middle connects to far_node.
                    connected_triples += 1

                    if G.has_edge(node, far_node):
                        triangles += 1

        result_q.put((shortest_path, num_paths, connected_triples, triangles))
        input_q.task_done()


process_count = mp.cpu_count()

print("CPUs found", process_count)

items_per_process = result.number_of_nodes() // process_count

print("Items per process", items_per_process)

results_queue: "mp.Queue[tuple[int,int,int,int]]" = mp.Queue()
inputs_queue: "mp.JoinableQueue[tuple[int,int]]" = mp.JoinableQueue()

# Children will do any work available
children = [
    Process(
        target=compute_metrics,
        args=(
            result,
            results_queue,
            inputs_queue,
        ),
    )
    for _ in range(process_count)
]


input_squares = [
    (x_start, x_start + items_per_process - 1)
    for x_start in range(0, result.number_of_nodes(), items_per_process)
]

for square in input_squares:
    inputs_queue.put(square)

print(f"Loaded {len(input_squares)} tasks")

for child in children:
    child.start()

print(f"Spawned {len(children)} subprocesses")

last_print = len(input_squares)

while last_print > 1:
    sleep(10)
    if inputs_queue.qsize() != last_print:
        last_print = inputs_queue.qsize()
        print(f"{last_print} tasks remain")

shortest_path = 0
num_paths = 0
total_triples = 0
total_triangles = 0

# close all children
print("Joining all children...")
inputs_queue.join()
for child in children:
    child.join()

print("Work complete")

# take from the queue
while not results_queue.empty():
    shortest_path_temp, num_paths_temp, num_triples, num_triangles = results_queue.get()
    shortest_path += shortest_path_temp
    num_paths += num_paths_temp
    total_triples += num_triples
    total_triangles += num_triangles

# for the shortest paths, we only want to count unique paths in our _undirected_ graph (ie a --> b but not b --> a).
# the current algorithm double counts every path for every process we spawn.
# the reason is that a process will count all paths from node a to any other node.
# so for every process, we count a --> b where a is in the process's task

print("Average Shortest Path Length", shortest_path / (2 * num_paths))

print("Average Clustering", (total_triangles * 3) / total_triples)

print_timing("Metrics")

# Avg Path length
# print(nx.algorithms.shortest_paths.average_shortest_path_length(result))

# Clustering coeff
# print(nx.algorithms.cluster.average_clustering(result))


# TODO: Make flag?
# Visualize the result
# nx.draw(result)
# plt.savefig("watts-strogatz.png")

print_timing("Visualization")
