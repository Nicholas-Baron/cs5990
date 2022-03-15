#!/usr/bin/python3

import matplotlib.pyplot as plt
import networkx as nx
from sys import exit
from time import time_ns
import gzip
from csv import reader

start = time_ns()

# set up timing functions
def print_timing(section: str):
    global start
    print(f"{section:25}", (time_ns() - start) / 1000000, "ms")
    start = time_ns()


# read in gz file
G = nx.Graph()

with gzip.open("com-amazon.ungraph.txt.gz", "rt") as f:
    for (node,) in list(reader(f))[1:]:
        n = node.split("\t")
        # handles info nodes at the start of list
        if len(n) >= 2:
            G.add_edge(n[0], n[1])


print_timing("Create Graph")
print(nx.info(G))

# calculate average degree
print_timing("Calculate Average Degree")
avg_degree = sum(d for (n, d) in nx.degree(G)) / float(G.number_of_nodes())
print(avg_degree)
