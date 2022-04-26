#!/usr/bin/python3

import networkx as nx
from itertools import product
from pprint import pprint
from typing import Dict, Tuple, List, Optional

g = nx.Graph()
g.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 3), (2, 3)])

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

for k in range(NODE_COUNT):
    for i in range(NODE_COUNT):
        if k == i:
            continue

        for j in range(NODE_COUNT):
            if k == j or j == i:
                continue

            print(f"{i} - {k} - {j}")

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


print(g)
print(g.edges())
pprint(paths)
pprint(dist)
