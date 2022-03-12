import matplotlib.pyplot as plt
from operator import itemgetter
import networkx as nx
from sys import exit

# Required:
# - Number of nodes (must be > 1)
# - Mean degree (must be >)
# - Parameter beta (between 0 and 1)

# TODO: Figure out the correct way to take the parameters.
# For now, just use stdin.

num_nodes: int = int(input("Number of Nodes"))
if num_nodes < 1:
    print("Number of nodes must be positive")
    exit(1)

mean_degree: float = float(input("Mean Degree"))

beta: float = float(input("Parameter Beta"))
if beta < 0 or beta > 1:
    print("beta must be between 0 and 1 (inclusive on both ends)")
    exit(2)
