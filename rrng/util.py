import pickle
import os.path
import numpy as np
from math import sqrt
from scipy.spatial import KDTree

def write_to_csv(G, pos, name1="graph.csv", name2="graph_loc.csv", dir="graph"):
    """
    - Write two files:
        - f1: edges of graphs
            |V|,|E|
            v1,v2,w12,
            ...
        - f2: location of nodes (for illustration)
    """
    path1 = os.path.join(dir, name1)
    path2 = os.path.join(dir, name2)
    f1 = open(path1, "w")
    f2 = open(path2, "w")

    nodes = sorted(G.nodes())
    f1.write("{},{},-1\n".format(G.number_of_nodes(), G.number_of_edges()))
    f2.write("{},{},-1\n".format(G.number_of_nodes(), G.number_of_edges()))
    for u in nodes:
        f2.write("{},{},{}\n".format(u, pos[u][0], pos[u][1]))
        for v in sorted(G[u]):
            if u < v:
                f1.write("{},{},{}\n".format(u, v, G[u][v]['weight']))

    f1.close()
    f2.close()
    return


def line_segment_intersection(p1, p2, p3, p4):
    """
    - Compute the intersect of two line segments if exists
    - Input:
        - p1, p2 (two end points of line segment 1; L1)
        - p3, p4 (two end points of line segment 2; L2)
    - Output:
        - (px, py) the intersect of two segments L1 and L2 if exists
        - None otherwise.
    """

    d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    if d == 0.0:
        return None

    intersect = [0.0, 0.0]
    u = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
    v = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
    if u < 0.0 or u > 1.0 or v < 0.0 or v > 1.0:
        return None

    px = p1[0] + u * (p2[0] - p1[0])
    py = p1[1] + u * (p2[1] - p1[1])
    if px == p1[0] and py == p1[1] or \
       px == p2[0] and py == p2[1] or \
       px == p3[0] and py == p3[1] or \
       px == p4[0] and py == p4[1]:
       return None

    return (px, py)


def compute_first_intersection(G, pos):
    """
    - Return the first intersect if exists
    - Input
        - Graph G
        - Position pos
    - Output
        - Intersect
    """
    computed = []
    for e1 in G.edges():
        p1, p2 = pos[e1[0]], pos[e1[1]]
        for e2 in G.edges():
            if e1 == e2:
                continue
            if len(set({e1[0], e1[1], e2[0], e2[1]})) < 4:
                continue
            p3, p4 = pos[e2[0]], pos[e2[1]]
            sg = line_segment_intersection(p1, p2, p3, p4)
            if sg is not None:
                computed.append((e1, e2, sg[0], sg[1]))
                break
        if len(computed) > 0:
            break
    return computed


def compute_first_collision_pair(G, idx2node, δ=5.0):
    nV, nE = G.number_of_nodes(), G.number_of_edges(0)
    pos = {n: (G.nodes[n]['x'], G.nodes[n]['y']) for n in G}
    
    # 座標作成
    pos = np.zeros((nV, 2))
    for idx in idx2node:
        n = idx2node[idx]
        pos[idx, 0] = G.nodes[n]['x']
        pos[idx, 1] = G.nodes[n]['y']
    tree = KDTree(pos)

    # 木にqueryを投げて近いノードを探す
    computed = []
    for idx in idx2node:
        n = idx2node[idx]
        p = pos[idx, :]
        di, li = tree.query(p, k=5, distance_upper_bound=δ)
        li_rev = [j for j in li if j != idx and j < nV]
        if li_rev:
            for elem in li_rev:
                ide = idx2node[elem]
            computed.append((idx, li_rev))
        if computed:
            break
    return computed


def merge(G, δ=5.0):
    nV, nE = G.number_of_nodes(), G.number_of_edges(0)
    idx2node = {idx: n for idx, n in enumerate(G.nodes())}
    computed = compute_first_collision_pair(G, idx2node, δ=δ)
    while computed:
        # merge V <- L [u0, u1, ...]
        Vid, L = computed[0]
        v = idx2node[Vid]
        vx = G.nodes[v]['x']
        vy = G.nodes[v]['y']
        for idx in L:
            if idx not in idx2node:
                continue
            u = idx2node[idx]

            # remove id and its node
            del idx2node[idx]

            # re-connect from ng(u) to v
            for uu in G.neighbors(u):
                if uu == v:
                    continue
                # 距離を計算して張り直し
                uux = G.nodes[uu]['x']
                uuy = G.nodes[uu]['y']
                dist = round(sqrt((vx - uux) ** 2 + (vy - uuy) ** 2), 3)
                G.add_edge(uu, v, weight=dist)

            # remove node
            G.remove_node(u)

        # compute next list
        idx2node = {idx: n for idx, n in enumerate(G.nodes())}
        computed = compute_first_collision_pair(G, idx2node, δ=δ)
    return G


def clean_up(G, verbose=False):
    nV, nE = G.number_of_nodes(), G.number_of_edges(0)
    pos = {n: (G.nodes[n]['x'], G.nodes[n]['y']) for n in G}
    computed = compute_first_intersection(G, pos)
    new_node_c = nV
    while computed:
        # edge update
        e1, e2, x, y = computed[0]
        u1, v1 = e1
        u2, v2 = e2

        # add intersection node
        G.add_node(new_node_c, x=x, y=y)
        pos[new_node_c] = (x, y)
        
        # remove (u1, v1), insert (u1, (x, y)) and ((x, y), v1) with new distances
        u1x, u1y = pos[u1]
        v1x, v1y = pos[v1]
        du1 = sqrt((u1x - x) ** 2 + (u1y - y) ** 2)
        dv1 = sqrt((v1x - x) ** 2 + (v1y - y) ** 2)
        G.remove_edge(u1, v1)
        G.add_edge(u1, new_node_c, weight=du1)
        G.add_edge(v1, new_node_c, weight=dv1)

        # remove (u2, v2), insert (u2, (x, y)) and ((x, y), v2) with new distances
        u2x, u2y = pos[u2]
        v2x, v2y = pos[v2]
        du2 = sqrt((u2x - x) ** 2 + (u2y - y) ** 2)
        dv2 = sqrt((v2x - x) ** 2 + (v2y - y) ** 2)
        G.remove_edge(u2, v2)
        G.add_edge(u2, new_node_c, weight=du2)
        G.add_edge(v2, new_node_c, weight=dv2)
        computed = compute_first_intersection(G, pos)

        # next iteration node number
        new_node_c += 1

    # G = merge(G, δ=5.)
    return G, pos