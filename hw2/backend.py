# No shebang since it should not be runnable
# Only functions that are needed by both the Twitter and Facebook scripts
import sys

from networkx import Graph
from networkx.algorithms.centrality.betweenness import betweenness_centrality

import gzip
from itertools import product, count
from math import ceil
from mpi4py import MPI
from pprint import pprint
from statistics import mean
from time import time_ns
from tqdm import tqdm
from typing import Dict, List
from heapq import heappush, heappop

start = time_ns()


# Print time with section name and reset internal timer
def print_timing(section: str):
    global start
    total_ms_taken = (time_ns() - start) // 1000000
    seconds_taken = total_ms_taken // 1000

    if seconds_taken > 0:
        print(f"{section:25} {seconds_taken:10} seconds")
    else:
        print(f"{section:25} {total_ms_taken:10} ms")

    start = time_ns()


# NOTE: Must specify a gzipped file
def load_graph(filename: str) -> Graph:
    g = Graph()

    assert filename.endswith(".txt.gz"), f"{filename} does not end in '.txt.gz'"

    print("Loading from", filename)

    with gzip.open(filename, "rt") as f:
        # We need to `strip()` to remove the newline at the end of the edge entry.
        # split on the space

        processed_lines = (
            tuple(int(node) for node in line.strip().split(" ")) for line in f
        )
        g.add_edges_from(edge for edge in processed_lines if len(edge) == 2)

    return g


def parallel_betweenness_centrality(g: Graph):
    betweenness = Dict.fromkeys(g, 0.0)
    nodes = g
    NODE_COUNT = len(nodes)
    # for parallelism, just divide the source nodes and deal with remainders.

    comm = MPI.COMM_WORLD
    num_proc = comm.Get_size()
    rank = comm.Get_rank()

    num_nodes_per_proc = ceil(NODE_COUNT / num_proc)
    num_nodes_per_last_proc = NODE_COUNT - (num_nodes_per_proc * (num_proc-1))

    # for s in tqdm(nodes, desc="Outer"):
    nodes = list(g)
    for off in range(num_nodes_per_proc):
        # single source shortest paths
        # unweighted, so just use BFS
        s = num_nodes_per_proc * rank + off

        if s in nodes:
            S_nodes_connected_to_s, P_path_nodes_of_all_s_to_S, sigma = get_paths_sigma(g, nodes[s])

            betweenness = summate_betweenness(betweenness, S_nodes_connected_to_s, P_path_nodes_of_all_s_to_S, sigma, nodes[s])

            # divide by 2 because undirected graph is expected
            for v in betweenness:
                betweenness[v] *= 0.5
            #
        for proc in range(num_proc):
            comm.allgather(betweenness)



    return betweenness


def get_paths_sigma(g, s):
    S_nodes_connected_to_s = []
    P_path_nodes_of_all_s_to_S = {}  # (partial?)Path dict of all nodes
    for v in g:
        P_path_nodes_of_all_s_to_S[v] = []
    # sigma = A betweenness 'slice' dict containing every node as key and every value as
    #         the respective count of paths calculated during this function.
    sigma = dict.fromkeys(g, 0.0)
    distance_dict_from_s_to_all = {}
    sigma[s] = 1.0  # <- betweenness to self is 1
    seen = {s: 0}  # <- This is the seen dictionary
    distance_heap = []  # heap as tuple(distance, node)
    heappush(distance_heap, (0, s, s))  # Push onto heap (init_dist (0), init node in count c,
    #                                                          source as pred, and source as dest v)
    while distance_heap:  # While the distance heap is not empty,
        (dist, pred, v) = heappop(distance_heap)
        if v in distance_dict_from_s_to_all:
            continue  # already searched this node.
        sigma[v] += sigma[pred]  # count predecessor paths (counts edge as to and from?)
        S_nodes_connected_to_s.append(v)
        distance_dict_from_s_to_all[v] = dist
        for w, edgedata in g[v].items():  # For each node connected to v,
            vw_dist = dist + 1  # update dist_dict accordingly (+1 per connecting edge)
            if w not in distance_dict_from_s_to_all and (
                    w not in seen or vw_dist < seen[w]):  # if w not in dist_d & path is shorter,
                seen[w] = vw_dist
                heappush(distance_heap, (vw_dist, v, w))  # Add next connection to investigate
                sigma[w] = 0.0  # Instantiate sigma for next connection v
                P_path_nodes_of_all_s_to_S[w] = [v]  # add to path dictionary?
            elif vw_dist == seen[w]:  # else if new path as short as old path,
                sigma[w] += sigma[v]
                P_path_nodes_of_all_s_to_S[w].append(v)
            #  else: its just a useless meandering path, skip it
    return S_nodes_connected_to_s, P_path_nodes_of_all_s_to_S, sigma


def summate_betweenness(betweenness, S, P, sigma, s):
    delta = dict.fromkeys(S, 0)
    while S:
        w = S.pop()
        coeff = (1 + delta[w]) / sigma[w]
        for v in P[w]:  # Sum paths that include v, weighted by coeff
            delta[v] += sigma[v] * coeff
        if w != s:  # Add the partial betweenness-es together
            betweenness[w] = delta[w] + betweenness[w]
    return betweenness


def print_centrality_data(filename: str, data: Dict[int, float]):
    # Print out to a local file the centrality measures for all the vertices.
    with open(filename, "w") as output:
        pprint(data, stream=output)

    # print five nodes with the top centrality values
    print("Top 5 nodes by centrality")
    for (node, centrality) in sorted(data.items(), reverse=True, key=lambda x: x[1])[
                              :5
                              ]:
        print(f"{node:5} {centrality:5.5}")

    # print the average of the centrality values of all nodes
    print("Centrality Average", mean(data.values()))
