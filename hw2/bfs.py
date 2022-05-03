#!/usr/bin/python3

from backend import print_timing
import networkx as nx

from collections import deque

# from mpi4py import MPI
from pprint import pprint
from sys import getsizeof
from typing import Dict, Tuple, Set, List

g = nx.Graph()

# Toy example (remove)
g.add_edges_from([(0, 4), (1, 4), (2, 3), (2, 5), (2, 6), (3, 4), (3, 5), (3, 6)])

NODE_COUNT = g.number_of_nodes()

# map source to map of destination to list of paths

INITIAL_VALUE = 10


# Returns a map of nodes to paths
def bfs(g: "nx.Graph", src: int) -> Dict[int, List[List[int]]]:
    result: Dict[int, List[List[int]]] = {src: []}
    frontier: deque[int] = deque()
    frontier.append(src)

    while len(frontier) > 0:
        visiting = frontier.popleft()

        existing_paths = result.get(visiting)
        existing_lengths = len(existing_paths[0]) if existing_paths else INITIAL_VALUE

        for neighbor in g.neighbors(visiting):
            # TODO: (dest, src) path is the same as (src, dest)

            if neighbor not in result:
                frontier.append(neighbor)
                result[neighbor] = (
                    [path + [visiting] for path in existing_paths]
                    if existing_paths
                    else [[]]
                )
            else:
                path_set = result.get(neighbor, [])
                if path_set == []:
                    continue

                new_paths_length = len(path_set[0]) + 1
                if new_paths_length < existing_lengths:
                    result[visiting] = [path + [neighbor] for path in path_set]
                elif new_paths_length == existing_lengths:
                    for path in [path + [neighbor] for path in path_set]:
                        if path not in result[visiting]:
                            result[visiting].append(path)

    return result


# Serial Breadth first search
paths: Dict[Tuple[int, int], List[List[int]]] = {
    (src, dest): path_set for src in g.nodes() for dest, path_set in bfs(g, src).items()
}

pprint(paths)

betweenness_centrality = {}

# Serial betweenness centrality
for node in g.nodes():
    centrality = 0.0
    for src in g.nodes():
        if node == src:
            continue

        for dest in g.nodes():
            if dest == src or node == dest:
                continue

            all_paths = paths.get((src, dest))
            if all_paths is None:
                continue

            paths_thru_node = sum(
                1 for path in all_paths for stop in path if stop == node
            )

            centrality += paths_thru_node / len(all_paths)

    betweenness_centrality[node] = centrality

pprint(betweenness_centrality)
