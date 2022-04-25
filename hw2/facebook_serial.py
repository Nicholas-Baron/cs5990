#!/usr/bin/python3

from backend import (
    load_graph,
    print_centrality_data,
    print_timing,
    serial_betweenness_centrality,
)

import networkx as nx

# Facebook dataset
# no parallelism

g = load_graph("facebook_combined.txt.gz")
print_timing("Loading Graph")

print(g)

centralities = serial_betweenness_centrality(g)
print_timing("Betweenness Centrality")

print_centrality_data("facebook_serial_raw_output.txt", centralities)
