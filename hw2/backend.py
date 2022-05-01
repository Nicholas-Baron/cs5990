# No shebang since it should not be runnable
# Only functions that are needed by both the Twitter and Facebook scripts
import sys

from networkx import Graph
from networkx.algorithms.centrality.betweenness import betweenness_centrality

import gzip
from itertools import product
from mpi4py import MPI
from pprint import pprint
from statistics import mean
from time import time_ns
from typing import Dict, List, Tuple

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


def parallel_betweenness_centrality(g: Graph) -> Dict[int, float]:
    # Initalization
    # INITIAL_VALUE was chosen by finding the largest diameter of our datasets and rounding up
    INITIAL_VALUE = 10
    NODE_COUNT = g.number_of_nodes()

    paths: Dict[Tuple[int, int], List[Tuple[int, ...]]] = {}

    for (u, v) in g.edges():
        paths[(u, v)] = [tuple()]
        # undirected means (u,v) is also (v,u)
        paths[(v, u)] = [tuple()]

    # Init
    print("Init paths: " + str(sys.getsizeof(paths)))

    def compute_paths(k: int, i: int, j: int) -> List[Tuple[int, ...]]:
        return [
            tuple(list(half1) + [k] + list(half2))
            for (half1, half2) in product(paths[(i, k)], paths[(k, j)])
        ]

    def update_paths(k: int, i: int, j: int):
        if (i, k) in paths and (k, j) in paths:
            source_path_len = len(paths[(i, k)][0]) + 1
            dest_path_len = len(paths[(k, j)][0]) + 1

            possible_new_path = source_path_len + dest_path_len

            if (i, j) not in paths:
                path_len = INITIAL_VALUE
            else:
                path_len = len(paths[(i, j)][0]) + 1

            if path_len > possible_new_path:
                paths[(i, j)] = compute_paths(k, i, j)
            elif path_len == possible_new_path:
                # TODO: check for duplicate paths
                paths[(i, j)] += compute_paths(k, i, j)

    comm = MPI.COMM_WORLD
    num_proc = comm.Get_size()
    rank = comm.Get_rank()

    # Divvy nodes and remainders between processors
    num_nodes_per_proc = NODE_COUNT // num_proc
    remainder_nodes = NODE_COUNT % num_proc

    def transmit_paths(off: int):
        for proc in range(num_proc):
            row = proc * num_nodes_per_proc + off

            for j, path_set in comm.bcast(
                {j: path_set for (i, j), path_set in paths.items() if i == row},
                root=proc,
            ).items():
                paths[(i, j)] = path_set

    # Serial Floyd-Warshall
    for k in range(NODE_COUNT):
        for off in range(num_nodes_per_proc):
            i = rank * num_nodes_per_proc + off
            if k == i:
                continue

            for j in range(NODE_COUNT):
                if k == j or j == i:
                    continue
                update_paths(k, i, j)

            transmit_paths(off)

        for off in range(remainder_nodes):
            i = (num_proc - 1) * num_nodes_per_proc + off
            for j in range(NODE_COUNT):
                if k == j or j == i:
                    continue
                update_paths(k, i, j)

    print("After Floyd paths: " + str(sys.getsizeof(paths)))

    # Parallel betweenness centrality

    centrality_results = {}

    def calculate_centrality(node: int) -> float:
        centrality = 0.0
        for src in g.nodes():
            if node == src:
                continue

            for dest in g.nodes():
                if dest == src or node == dest:
                    continue

                all_paths = paths.get((src, dest))
                if all_paths is None:
                    continue

                paths_thru_node = sum(
                    1 for path in all_paths for stop in path if stop == node
                )

                centrality += paths_thru_node / len(all_paths)
        return centrality

    for off in range(num_nodes_per_proc):
        node = rank * num_nodes_per_proc + off
        centrality_results[node] = calculate_centrality(node)

    centrality_results = {
        node: centrality
        for proc_result in comm.allgather(centrality_results)
        for (node, centrality) in proc_result.items()
    }

    # compute remaining nodes
    for off in range(remainder_nodes):
        node = (num_proc - 1) * num_nodes_per_proc + off
        centrality_results[node] = calculate_centrality(node)

    return centrality_results


def serial_betweenness_centrality(g: Graph) -> Dict[int, float]:
    # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.betweenness_centrality.html
    return betweenness_centrality(g, normalized=False)


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
