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
    print(f"{section:25}", (time_ns() - start) // 1000000, "ms")
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
avg_degree = sum(d for (n, d) in nx.degree(G)) / float(G.number_of_nodes())
print(avg_degree)

print_timing("Calculate Average Degree")

# TODO: this is overengineered b/c every process only works on 1 task. `input_q` should be replaced with the input
def compute_metrics(
    G,
    result_q: "mp.Queue[tuple[int, int, int]]",
    input_q: "mp.JoinableQueue[tuple[int,int]]",
):
    nodes = list(G)
    while not input_q.empty():
        x_endpoints = input_q.get()

        shortest_path = 0
        connected_triples = 0
        triangles = 0
        for node in nodes[x_endpoints[0] : x_endpoints[1]]:

            shortest_path += sum(nx.shortest_path_length(G, node).values())

            # for clustering, we need 2 more nodes.
            # this is because clustering tries to distinguish
            # between triangles (n1, n2, n3 all connected to each other)
            # and triples (n1, n2, n3 have some direct connections between them)

            for middle in G.neighbors(node):
                # we only care about forward connections
                # because all triples/triangles will be processed according to their least element
                if middle <= node:
                    continue

                # get a third node from somewhere after middle
                for far_node in G.neighbors(middle):
                    if far_node <= middle:
                        continue

                    # at this point, we know that node connects to middle
                    # and middle connects to far_node.
                    connected_triples += 1

                    if G.has_edge(node, far_node):
                        triangles += 1

        result_q.put((shortest_path, connected_triples, triangles))
        input_q.task_done()


process_count = mp.cpu_count()

print("CPUs found", process_count)

items_per_process = G.number_of_nodes() // process_count

print("Items per process", items_per_process)

results_queue: "mp.Queue[tuple[int,int,int]]" = mp.Queue()
inputs_queue: "mp.JoinableQueue[tuple[int,int]]" = mp.JoinableQueue()

# Children will do any work available
children = [
    Process(
        target=compute_metrics,
        args=(
            G,
            results_queue,
            inputs_queue,
        ),
    )
    for _ in range(process_count)
]


input_squares = [
    (x_start, x_start + items_per_process - 1)
    for x_start in range(0, G.number_of_nodes(), items_per_process)
]

for square in input_squares:
    inputs_queue.put(square)

print(f"Loaded {len(input_squares)} tasks")

for child in children:
    child.start()

print(f"Spawned {len(children)} subprocesses")

last_print = len(input_squares)

while last_print > 1:
    sleep(10)
    if inputs_queue.qsize() != last_print:
        last_print = inputs_queue.qsize()
        print(f"{last_print} tasks remain")

shortest_path = 0
total_triples = 0
total_triangles = 0

# close all children
print("Joining all children...")
inputs_queue.join()
for child in children:
    child.join()

print("Work complete")

# take from the queue
while not results_queue.empty():
    shortest_path_temp, num_triples, num_triangles = results_queue.get()
    shortest_path += shortest_path_temp
    total_triples += num_triples
    total_triangles += num_triangles

# for the shortest paths, we only want to count unique paths in our _undirected_ graph (ie a --> b but not b --> a).
# the current algorithm double counts every path for every process we spawn.
# the reason is that a process will count all paths from node a to any other node.
# so for every process, we count a --> b where a is in the process's task
shortest_path /= 2

print("Average Shortest Path Length", shortest_path / G.number_of_nodes())

print("Average Clustering", (total_triangles * 3) / total_triples)

print_timing("Metrics")
