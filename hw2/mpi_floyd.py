#!/usr/bin/python3

from backend import print_timing
import networkx as nx
from mpi4py import MPI
from pprint import pprint
from typing import Dict, Tuple, Set


comm = MPI.COMM_WORLD
num_proc = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    print(f"Running on {num_proc} processors")

print("Rank", rank)

g = nx.Graph()

# Toy example (remove)
g.add_edges_from(
    [
        (0, 4),
        (1, 4),
        (2, 3),
        (2, 5),
        (2, 6),
        (3, 4),
        (3, 5),
        (3, 6)
    ]
)

NODE_COUNT = g.number_of_nodes()

# Initialize distance matrix with diameter (7 for twitter, 8 for facebook)
INITIAL_VALUE = 8
dist = [[INITIAL_VALUE for _ in range(NODE_COUNT)] for _ in range(NODE_COUNT)]

# Initialize paths dictionary (key: (source, dest) value: set of tuple-funkiness as set of nodes between source & dest
paths: Dict[Tuple[int, int], Set[Tuple[int, ...]]] = {}

# For edge's source and dest, distance = 1. Instantiate paths[source, dest] as empty path list
for (u, v) in g.edges():
    dist[u][v] = 1
    paths[(u, v)] = {tuple()}
    # undirected means (u,v) is also (v,u)
    dist[v][u] = 1
    paths[(v, u)] = {tuple()}

# Set diagonal (distance between node and self is 0)
for v in range(NODE_COUNT):
    dist[v][v] = 0

if rank == 0:
    print_timing("Initalization")

# Divvy nodes and remainders between processors
num_nodes_per_proc = NODE_COUNT // num_proc
remainder_nodes = NODE_COUNT % num_proc


def compute_distance(k: int, off: int) -> int:
    i = rank * num_nodes_per_proc + off
    for j in range(NODE_COUNT):
        if k == j or j == i:
            continue

        possible_new_path = dist[i][k] + dist[k][j]
        if dist[i][j] > possible_new_path:
            dist[i][j] = possible_new_path
    return i


def trasmit_data(i: int, off: int):
    for proc in range(num_proc):
        # Row that is transmitted
        index_to_transmit = proc * num_nodes_per_proc + off

        sent_row = comm.bcast(dist[index_to_transmit], root=proc)
        # apply the new row
        dist[index_to_transmit] = sent_row
        for (i, val) in enumerate(sent_row):
            dist[i][index_to_transmit] = val


# For each intermediate node k,
for k in range(NODE_COUNT):
    for off in range(num_nodes_per_proc):
        # Offset i based on processor amount
        i = compute_distance(k, off)
        trasmit_data(i, off)

    # process remainders
    if rank == num_proc - 1:
        for off in range(remainder_nodes):
            i = compute_distance(k, off)

    # transmit remainders
    for off in range(remainder_nodes):
        index_to_transmit = (num_proc - 1) * num_nodes_per_proc + off
        # Broadcast from the last processor (handles the remainders)
        sent_row = comm.bcast(dist[index_to_transmit], root=num_proc - 1)
        # apply the new row
        dist[index_to_transmit] = sent_row
        for (i, val) in enumerate(sent_row):
            dist[i][index_to_transmit] = val


if rank == 0:
    print_timing("Floyd-Warshall")
    pprint(dist)
