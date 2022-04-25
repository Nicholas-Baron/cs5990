#!/usr/bin/python3

from backend import load_graph, serial_betweenness_centrality, print_timing
import networkx as nx
from pprint import pprint

# Facebook dataset
# no parallelism

g = load_graph("facebook_combined.txt.gz")
print_timing("Loading Graph")

print(g)

centralities = serial_betweenness_centrality(g)
print_timing("Betweenness Centrality")

pprint(centralities)
