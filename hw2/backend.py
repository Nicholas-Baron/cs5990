# No shebang since it should not be runnable
# Only functions that are needed by both the Twitter and Facebook scripts

from networkx import Graph
from networkx.algorithms.centrality.betweenness import betweenness_centrality

from pprint import pprint
from statistics import mean
from time import time_ns
from typing import Dict
import gzip

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
    # 1. Initalize the dist matrix and path dictionary
    # Note: since our graph is undirected, we need to do (u,v) and (v,u)
    # 2. Get info from MPI
    # 3. Loop over k
    # 3a. Do in parallel
    # 3aa. Calculate distance in 1 row
    # 3ab. Update path dictionary
    # 3ac. Transmit updates to everyone
    # 4. Calculate betweenness_centrality in parallel
    pass


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
