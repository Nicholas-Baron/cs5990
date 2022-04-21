#!/usr/bin/python3

from backend import load_graph, print_timing
import networkx as nx

# Twitter dataset
# no parallelism

g = load_graph("twitter_combined.txt.gz")
print_timing("Loading graph")
print(g)
