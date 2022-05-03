#!/usr/bin/python3

from backend import (
    betweenness_centrality,
    load_graph,
    print_centrality_data,
    print_timing,
)

import networkx as nx

# Facebook dataset
# with parallelism

g = load_graph("facebook_combined.txt.gz")
print_timing("Loading Graph")

print(g)

centralities = betweenness_centrality(g)
print_timing("Betweenness Centrality")

print_centrality_data("facebook_raw_output.txt", centralities)
