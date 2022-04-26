#!/usr/bin/python3

from backend import print_timing
import networkx as nx
from itertools import product
from pprint import pprint
from typing import Dict, Tuple, List, Optional

g = nx.watts_strogatz_graph(1000, 2, 0.5)

NODE_COUNT = g.number_of_nodes()

INITIAL_VALUE = 500
dist = [[INITIAL_VALUE for _ in range(NODE_COUNT)] for _ in range(NODE_COUNT)]

paths: Dict[tuple[int, int], set[tuple[int, ...]]] = {}


for (u, v) in g.edges():
    dist[u][v] = 1
    paths[(u, v)] = {tuple()}
    # undirected means (u,v) is also (v,u)
    dist[v][u] = 1
    paths[(v, u)] = {tuple()}

for v in range(NODE_COUNT):
    dist[v][v] = 0

print_timing("Initalization")

for k in range(NODE_COUNT):
    for i in range(NODE_COUNT):
        if k == i:
            continue

        for j in range(NODE_COUNT):
            if k == j or j == i:
                continue

            possible_new_path = dist[i][k] + dist[k][j]
            if dist[i][j] > possible_new_path:
                dist[i][j] = possible_new_path
                paths[(i, j)] = {
                    tuple(list(half1) + [k] + list(half2))
                    for (half1, half2) in product(paths[(i, k)], paths[(k, j)])
                }
            elif dist[i][j] == possible_new_path:
                paths[(i, j)] |= {
                    tuple(list(half1) + [k] + list(half2))
                    for (half1, half2) in product(paths[(i, k)], paths[(k, j)])
                }

print_timing("Floyd-Warshall")

# between centrality
for node in g.nodes():
    centrality = 0.0
    for src in g.nodes():
        if node == src:
            continue

        for dest in g.nodes():
            if dest == src or node == dest:
                continue

            all_paths = paths[(src, dest)]
            paths_thru_node = sum(
                1 for path in all_paths for stop in path if stop == node
            )

            centrality += paths_thru_node / len(all_paths)

    print(f"Betweenness centrality for {node}: {centrality}")

print_timing("Betweenness centrality")
