#!/usr/bin/python3

from backend import load_graph
import networkx as nx

# Facebook dataset
# no parallelism

g = load_graph("facebook_combined.txt.gz")
print(g)
