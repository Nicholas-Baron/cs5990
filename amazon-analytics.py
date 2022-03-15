#!/usr/bin/python3

import matplotlib.pyplot as plt
import networkx as nx
from sys import exit
from time import time_ns
import gzip
import csv

# set up timing functions
def print_timing(section: str):
        global start
        print(f"{section:25}", (time_ns() - start) / 1000000, "ms")
        start = time_ns()

start = time_ns()

# read in gz file
f = gzip.open('com-amazon.ungraph.txt.gz', 'rt')
nodereader = csv.reader(f)
nodes = [n for n in nodereader][1:]
node_names = set()
# create graph
G = nx.Graph()

for node in nodes:
        n = node[0].split("\t")
        # handles info nodes at the start of list
        if len(n) < 2:
                continue
        if n[0] not in node_names:
                node_names.add(n[0])
                G.add_node(n[0])
        if n[1] not in node_names:
                node_names.add(n[1])
                G.add_node(n[1])
        G.add_edge(n[0], n[1])

print_timing("Create Graph")
print(nx.info(G))

# calculate average degree
print_timing("Calculate Average Degree")
avg_degree = sum([d for (n,d) in nx.degree(G)]) / float(G.number_of_nodes())
print(avg_degree)