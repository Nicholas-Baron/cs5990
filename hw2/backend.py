# No shebang since it should not be runnable
# Only functions that are needed by both the Twitter and Facebook scripts

from networkx import Graph
from networkx.algorithms.centrality.betweenness import betweenness_centrality

from time import time_ns
from typing import Dict
import gzip

start = time_ns()


# Print time with section name and reset internal timer
def print_timing(section: str):
    global start
    total_ms_taken = (time_ns() - start) // 1000000
    seconds_taken = total_ms_taken // 1000
    print(f"{section:25} {seconds_taken:10} seconds")
    start = time_ns()


# NOTE: Must specify a gzipped file
def load_graph(filename: str) -> Graph:
    g = Graph()

    assert filename.endswith(".txt.gz"), f"{filename} does not end in '.txt.gz'"

    print("Loading from", filename)

    with gzip.open(filename, "rt") as f:
        # We need to `strip()` to remove the newline at the end of the edge entry.
        # split on the space

        processed_lines = (tuple(node.strip().split(" ")) for node in f)
        g.add_edges_from(edge for edge in processed_lines if len(edge) == 2)

    return g


def parallel_betweenness_centrality(g: Graph) -> Dict[int, float]:
    # Use MPI and partition?
    pass


def serial_betweenness_centrality(g: Graph) -> Dict[int, float]:
    # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.betweenness_centrality.html
    return betweenness_centrality(g)
