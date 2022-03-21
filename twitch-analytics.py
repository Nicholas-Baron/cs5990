#!/usr/bin/python3

import matplotlib.pyplot as plt
import csv
import networkx as nx
from sys import exit
from time import time_ns
from csv import reader

start = time_ns()

# set up timing functions
def print_timing(section: str):
    global start
    print(f"{section:25}", (time_ns() - start) / 1000000, "ms")
    start = time_ns()


# read in gz file
G = nx.Graph()

# Read in the edge list file
with open('large_twitch_edges.csv', 'r') as nodecsv:
    reader = csv.reader(nodecsv)
    next(reader)
    for n in reader:
        G.add_edge(n[0], n[1])

print_timing("Create Graph")
print(nx.info(G))

# calculate average degree
print_timing("Calculate Average Degree")
avg_degree = sum(d for (n, d) in nx.degree(G)) / float(G.number_of_nodes())
print(avg_degree)
