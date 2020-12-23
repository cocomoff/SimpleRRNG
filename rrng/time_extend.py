import os.path
import networkx as nx

def time_extend(G, T, edge_name="graph_tw_T{}_edge.csv", dict_name="graph_tw_T{}_dict.csv", dir="./graph/"):
    nodes_with_time = set({})
    edges_with_time = set({})
    TG = nx.DiGraph()
    for t in range(T):
        for n in G.nodes():
            TG.add_node((n, t))

    # (t, t+1)の辺を貼る
    for t in range(T - 1):
        for n in G.nodes():
            fn = (n, t)
            for u in G.neighbors(n):
                tu = (u, t + 1)
                TG.add_edge(fn, tu, weight=G[n][u]['weight'])


    # check
    total = 0
    for n in G.nodes():
        tn = G.degree(n) * (T - 1)
        total += tn

    print("> |V(TG)|={}, |E(TG)|={}".format(TG.number_of_nodes(), TG.number_of_edges()))
    print("> total={}".format(total))

    # dictionary (mapping)
    id2node = {idx: n for (idx, n) in enumerate(TG.nodes())}
    node2id = {n:idx for (idx, n) in id2node.items()}
    dict_name = os.path.join(dir, dict_name.format(T))
    edge_name = os.path.join(dir, edge_name.format(T))
    with open(dict_name, "w") as f:
        for n in range(TG.number_of_nodes()):
            nn, tn = id2node[n]
            f.write("{},{},{}\n".format(n, nn, tn))
    with open(edge_name, "w") as f:
        f.write("{},{},-3\n".format(TG.number_of_nodes(), TG.number_of_edges()))
        for n in range(TG.number_of_nodes()):
            for u in TG[id2node[n]]:
                f.write("{},{},{}\n".format(n, node2id[u], TG[id2node[n]][u]['weight']))

    return TG