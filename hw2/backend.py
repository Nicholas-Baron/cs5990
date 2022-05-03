# No shebang since it should not be runnable
# Only functions that are needed by both the Twitter and Facebook scripts
import sys

from networkx import Graph

from collections import deque
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


def betweenness_centrality(g: Graph) -> Dict[int, float]:
    # Initalization
    # INITIAL_VALUE was chosen by finding the largest diameter of our datasets and rounding up
    INITIAL_VALUE = 10

    # Returns a map of nodes to paths
    def bfs(g: Graph, src: int) -> Dict[int, List[List[int]]]:
        result: Dict[int, List[List[int]]] = {src: []}
        frontier: deque[int] = deque()
        frontier.append(src)

        while len(frontier) > 0:
            visiting = frontier.popleft()

            existing_paths = result.get(visiting)
            existing_lengths = (
                len(existing_paths[0]) if existing_paths else INITIAL_VALUE
            )

            for neighbor in g.neighbors(visiting):
                # TODO: (dest, src) path is the same as (src, dest)

                if neighbor not in result:
                    frontier.append(neighbor)
                    result[neighbor] = (
                        [path + [visiting] for path in existing_paths]
                        if existing_paths
                        else [[]]
                    )
                else:
                    path_set = result.get(neighbor, [])
                    if path_set == []:
                        continue

                    new_paths_length = len(path_set[0]) + 1
                    if new_paths_length < existing_lengths:
                        result[visiting] = [path + [neighbor] for path in path_set]
                    elif new_paths_length == existing_lengths:
                        for path in [path + [neighbor] for path in path_set]:
                            if path not in result[visiting]:
                                result[visiting].append(path)

        return result

    # Serial Breadth first search
    paths: Dict[Tuple[int, int], List[List[int]]] = {
        (src, dest): path_set
        for src in g.nodes()
        for dest, path_set in bfs(g, src).items()
    }

    print_timing("BFS")

    # Parallel betweenness centrality
    comm = MPI.COMM_WORLD
    num_proc = comm.Get_size()
    rank = comm.Get_rank()
    if rank == 0:
        print("Running on", num_proc, "processors")

    # Divvy nodes and remainders between processors
    num_nodes_per_proc = g.number_of_nodes() // num_proc
    remainder_nodes = g.number_of_nodes() % num_proc

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

    centrality_results = {}
    for off in range(num_nodes_per_proc):
        node = rank * num_nodes_per_proc + off
        centrality_results[node] = calculate_centrality(node)

    print_timing("betweenness parallel")

    centrality_results = {
        node: centrality
        for proc_result in comm.allgather(centrality_results)
        for (node, centrality) in proc_result.items()
    }

    print_timing("betweenness collection")

    # compute remaining nodes
    for off in range(remainder_nodes):
        node = (num_proc - 1) * num_nodes_per_proc + off
        centrality_results[node] = calculate_centrality(node)

    print_timing("betweenness remainder")

    return centrality_results


def print_centrality_data(filename: str, data: Dict[int, float]):
    # Only do this on rank 0 process
    if MPI.COMM_WORLD.Get_rank() != 0:
        return

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
