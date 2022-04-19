#!/usr/bin/python3

from backend import load_graph
import networkx as nx

# Twitter dataset
# no parallelism

g = load_graph("twitter_combined.txt.gz")
print(g)
