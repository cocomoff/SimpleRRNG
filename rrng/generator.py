# build random road network
#
# 1. randomly sample location points
# 2. compute pair-wise shortest paths
# 3. keep pairs if its length < 1.5 x (ST)

import numpy as np
import networkx as nx
import numpy.random as npr
import numpy.linalg as npl
from collections import defaultdict


def generate(Dx, Dy, N, coeff):
    xy = np.random.rand(N, 2)
    xy[:, 0] *= Dx
    xy[:, 1] *= Dy

    mindist = float("Inf")
    distlist = []
    for i in range(N):
        for j in range(i + 1, N):
            dij = npl.norm(xy[i, :] - xy[j, :])
            distlist.append((i, j, dij))
            mindist = min(mindist, dij)
    distlist = sorted(distlist, key=lambda x: x[2])
    
    # min ST and 1.5x procedure
    G = nx.Graph()
    reminder = []
    ijdij = distlist[0]
    reminder.append((ijdij[0], ijdij[1]))
    distlist.remove(ijdij)

    G.add_edge(ijdij[0], ijdij[1], weight=ijdij[2])
    for ijdij in distlist:
        # check already connected
        u, v, duv = ijdij
        try:
            pathuv = nx.shortest_path(G, u, v, weight='weight')
        except nx.exception.NodeNotFound as e:
            pathuv = []
            pass
        except nx.exception.NetworkXNoPath as e:
            pathuv = []
            pass
        finally:
            if not pathuv:
                G.add_edge(u, v, weight=duv)
            else:
                dpathuv = nx.shortest_path_length(G, u, v, weight='weight')
                if dpathuv > duv * coeff:
                    G.add_edge(u, v, weight=duv)

    # set position
    for n in G.nodes():
        G.nodes()[n]['x'] = xy[n, 0]
        G.nodes()[n]['y'] = xy[n, 1]

    # output
    print("Output: |V|={}, |E|={}".format(G.number_of_nodes(), G.number_of_edges()))
    return G, xy