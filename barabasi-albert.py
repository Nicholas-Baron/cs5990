#!/usr/bin/python3

from __future__ import annotations

from math import isqrt
import networkx as nx
from sys import exit
from random import choice, random
from time import time_ns, sleep

import multiprocessing as mp
from multiprocessing import Process

# Number of starting nodes |V|, ??
# Required:
# - Number of starting nodes (must be > 1)
# - Number of created edges per new node (must be less than # starting nodes)
# - Iterations (Time)

# TODO: Figure out the correct way to take the parameters.
# For now, just use stdin.

num_nodes: int = int(input("Number of Starting Nodes: "))
if num_nodes < 1:
    print("Number of nodes must be positive")
    exit(1)

expected_connections: int = int(
    input("Number of possible created edges per new node: ")
)
if expected_connections > num_nodes or expected_connections < 1:
    print(
        "Must be less than the number of starting nodes and must be a positive integer"
    )
    exit(2)

time: int = int(input("Number of times the algorithm will be run: "))
if time < 1:
    print("Must be a positive integer")
    exit(3)

start = time_ns()


def print_timing(section: str):
    global start
    print(f"{section:25}", (time_ns() - start) // 1000000, "ms")
    start = time_ns()


#  G = A Graph G(V0, E0) where |V0| = m0 and degree average is greater than or equal to 1.
g = nx.grid_2d_graph(isqrt(num_nodes), isqrt(num_nodes))


#  for 1 to t, create node. while new connections not reached,
for i in range(time):
    # calculate degree average
    degree_average = sum(d for (n, d) in nx.degree(g)) / float(g.number_of_nodes())

    # create new node
    new_node = num_nodes + i + 1
    g.add_node(new_node)

    while g.degree(new_node) != expected_connections:
        # vk = Select a node from V uniformly at random.
        rand_node = choice(list(g))

        # if rewiring e(vi , vj) to e(vi , vk) does not create loops in the graph or multiple edges between vi and vk then
        if rand_node == new_node or rand_node in g.neighbors(new_node):
            continue

        # richer get richer
        if random() > g.degree(rand_node) / degree_average:
            g.add_edge(new_node, rand_node)

print_timing("Create edges")


#  Return G(V, E)
