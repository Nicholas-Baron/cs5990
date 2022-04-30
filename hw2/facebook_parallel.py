#!/usr/bin/python3

from backend import (
    load_graph,
    parallel_betweenness_centrality,
    print_centrality_data,
    print_timing,
)

import networkx as nx

# Facebook dataset
# with parallelism

g = load_graph("facebook_combined.txt.gz")
print_timing("Loading Graph")

print(g)

centralities = parallel_betweenness_centrality(g)
print_timing("Betweenness Centrality")

print_centrality_data("facebook_parallel_raw_output.txt", centralities)
