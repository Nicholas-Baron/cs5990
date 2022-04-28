#!/usr/bin/python3

from backend import print_timing
import networkx as nx
from mpi4py import MPI
from pprint import pprint

comm = MPI.COMM_WORLD
num_proc = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    print(f"Running on {num_proc} processors")

print("Rank", rank)

g = nx.Graph()
g.add_edges_from(
    [
        (0, 4),
        (1, 4),
        (2, 3),
        (2, 5),
        (3, 4),
        (3, 5),
    ]
)

NODE_COUNT = g.number_of_nodes()

INITIAL_VALUE = 500
dist = [[INITIAL_VALUE for _ in range(NODE_COUNT)] for _ in range(NODE_COUNT)]

for (u, v) in g.edges():
    dist[u][v] = 1
    # undirected means (u,v) is also (v,u)
    dist[v][u] = 1

for v in range(NODE_COUNT):
    dist[v][v] = 0

if rank == 0:
    print_timing("Initalization")


num_nodes_per_proc = NODE_COUNT // num_proc
remainder_nodes = NODE_COUNT % num_proc


for k in range(NODE_COUNT):
    for off in range(num_nodes_per_proc):
        i = rank * num_nodes_per_proc + off
        for j in range(NODE_COUNT):
            if k == j or j == i:
                continue

            possible_new_path = dist[i][k] + dist[k][j]
            if dist[i][j] > possible_new_path:
                dist[i][j] = possible_new_path

        for proc in range(num_proc):
            index_to_transmit = proc * num_nodes_per_proc + off
            if index_to_transmit >= len(dist):
                print(
                    "rank",
                    rank,
                    "proc",
                    proc,
                    "num_nodes_per_proc",
                    num_nodes_per_proc,
                    "off",
                    off,
                )
            sent_row = comm.bcast(dist[index_to_transmit], root=proc)
            # apply the new row
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

    # transmit remainders
    for off in range(remainder_nodes):
        index_to_transmit = (num_proc - 1) * num_nodes_per_proc + off
        if index_to_transmit >= len(dist):
            print(
                "rank",
                rank,
                "proc",
                proc,
                "num_nodes_per_proc",
                num_nodes_per_proc,
                "off",
                off,
            )
        sent_row = comm.bcast(dist[index_to_transmit], root=num_proc - 1)
        # apply the new row
        dist[index_to_transmit] = sent_row
        for (i, val) in enumerate(sent_row):
            dist[i][index_to_transmit] = val


if rank == 0:
    print_timing("Floyd-Warshall")
    pprint(dist)
