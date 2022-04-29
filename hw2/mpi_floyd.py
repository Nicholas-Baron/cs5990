#!/usr/bin/python3

from backend import print_timing
from itertools import product
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
g.add_edges_from([(0, 4), (1, 4), (2, 3), (2, 5), (2, 6), (3, 4), (3, 5), (3, 6)])

NODE_COUNT = g.number_of_nodes()

# Initialize distance matrix with diameter (7 for twitter, 8 for facebook)
INITIAL_VALUE = 8
dist = [[INITIAL_VALUE for _ in range(NODE_COUNT)] for _ in range(NODE_COUNT)]

# Initialize paths dictionary (key: (source, dest) value: set of tuple-funkiness as set of nodes between source & dest
paths: Dict[Tuple[int, int], Set[Tuple[int, ...]]] = {
    (u, v): set() for (u, v) in product(range(NODE_COUNT), range(NODE_COUNT))
}


# For edge's source and dest, distance = 1. Instantiate paths[source, dest] as empty path list
# Initialize shape of paths (This will be huge, can we fix?)
for (u, v) in g.edges():
    dist[u][v] = 1
    # undirected means (u,v) is also (v,u)
    dist[v][u] = 1

    paths[(u, v)] = {tuple()}
    paths[(v, u)] = {tuple()}

# Set diagonal (distance between node and self is 0)
for v in range(NODE_COUNT):
    dist[v][v] = 0

if rank == 0:
    print_timing("Initalization")

# Divvy nodes and remainders between processors
num_nodes_per_proc = NODE_COUNT // num_proc
remainder_nodes = NODE_COUNT % num_proc

# For each intermediate node k,
for k in range(NODE_COUNT):
    for off in range(num_nodes_per_proc):
        # Offset i based on processor amount
        i = rank * num_nodes_per_proc + off
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

        for proc in range(num_proc):
            # Row that is transmitted
            index_to_transmit = proc * num_nodes_per_proc + off
            # Debug statement for index out of range error
            # if index_to_transmit >= len(dist):
            #     print(
            #         "rank",
            #         rank,
            #         "proc",
            #         proc,
            #         "num_nodes_per_proc",
            #         num_nodes_per_proc,
            #         "off",
            #         off,
            #     )
            dict_to_send = {
                (i, j): path_set
                for (i, j), path_set in paths.values()
                if i == index_to_transmit
            }
            for (i, j), path_set in comm.bcast(dict_to_send, root=proc):
                paths[(i, j)] = path_set
            # apply the new row
            sent_row = comm.bcast(dist[index_to_transmit], root=proc)
            dist[index_to_transmit] = sent_row
            for (i, val) in enumerate(sent_row):
                dist[i][index_to_transmit] = val

    # process remainders
    if rank == num_proc - 1:
        for off in range(remainder_nodes):
            i = rank * num_nodes_per_proc + off
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

    # transmit remainders
    for off in range(remainder_nodes):
        index_to_transmit = (num_proc - 1) * num_nodes_per_proc + off
        # Debug for index out of range error
        # if index_to_transmit >= len(dist):
        #     print(
        #         "rank",
        #         rank,
        #         "proc",
        #         proc,
        #         "num_nodes_per_proc",
        #         num_nodes_per_proc,
        #         "off",
        #         off,
        #     )
        # Broadcast from the last processor (handles the remainders)
        dict_to_send = {
            (i, j): path_set
            for ((i, j), path_set) in paths.values()
            if i == index_to_transmit
        }
        for (i, j), path_set in comm.bcast(dict_to_send, root=proc).values():
            paths[(i, j)] = path_set
        # apply the new row
        sent_row = comm.bcast(dist[index_to_transmit], root=num_proc - 1)
        dist[index_to_transmit] = sent_row
        for (i, val) in enumerate(sent_row):
            dist[i][index_to_transmit] = val

if rank == 0:
    print_timing("Floyd-Warshall")
    pprint(dist)
    pprint(paths)
