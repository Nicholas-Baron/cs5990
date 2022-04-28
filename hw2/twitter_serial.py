#!/usr/bin/python3

from backend import load_graph, print_timing
import networkx as nx

# Twitter dataset
# no parallelism

g = load_graph("twitter_combined.txt.gz")
print_timing("Loading graph")
print(g)
import networkx as nx

centralities = serial_betweenness_centrality(g)
print_timing("Betweenness Centrality")

print_centrality_data("twitter_serial_raw_output.txt", centralities)