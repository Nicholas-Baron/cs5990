# No shebang since it should not be runnable
# Only functions that are needed by both the Twitter and Facebook scripts

from networkx import Graph
from time import time_ns
from typing import Dict
import gzip

start = time_ns()


# Print time with section name and reset internal timer
def print_timing(section: str):
    global start
    print(f"{section:25}", (time_ns() - start) / 1000000, "ms")
    start = time_ns()


# NOTE: Must specify a gzipped file
def load_graph(filename: str) -> Graph:
    g = Graph()

    assert filename.endswith(".txt.gz"), f"{filename} does not end in '.txt.gz'"

    with gzip.open(filename, "rt") as f:
        # We need to `strip()` to remove the newline at the end of the edge entry.
        # split on the space

        # processed_lines = (tuple(node.strip().split(" ")) for node in f)
        # print(processed_lines)
        # g.add_edges_from(edge for edge in processed_lines if len(edge) == 2)

        for node in f:
            n = node.strip().split(" ")
            if len(n) >= 2:
                g.add_edge(n[0], n[1])
                if len(n) > 2:
                    print(n)

    return g


def parallel_betweenness_centrality(g: Graph) -> Dict[int, float]:
    # Use MPI and partition?
    pass


def serial_betweenness_centrality(g: Graph) -> Dict[int, float]:
    # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.betweenness_centrality.html
    pass
