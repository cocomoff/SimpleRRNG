import numpy as np
import networkx as nx
from rrng.time_extend import time_extend

if __name__ == '__main__':
    gname = "./graph/graph.csv"
    edges = np.loadtxt(gname, delimiter=",")
    nV = int(edges[0][0])
    nE = int(edges[0][1])
    edges = edges[1:, :]

    G = nx.Graph()
    for (u, v, wuv) in edges:
        u = int(u)
        v = int(v)
        G.add_node(u)
        G.add_node(v)
        G.add_edge(u, v, weight=wuv)

    print("read data: |V|={}, |E|={}".format(nV, nE))
    print("Graph (G): |V|={}, |E|={}".format(G.number_of_nodes(), G.number_of_edges()))
    TG = time_extend(G, T=10)
    print("T-Graph  : |V|={}, |E|={}".format(TG.number_of_nodes(), TG.number_of_edges()))
