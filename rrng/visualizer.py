import os.path
import networkx as nx
import matplotlib.pyplot as plt


def visualize(G, pos, name="output.png", dir="./output", H=5, label=True):
    fpath = os.path.join(dir, name)
    print(fpath)

    xseq = [pos[n][0] for n in G.nodes()]
    yseq = [pos[n][1] for n in G.nodes()]
    mx, my = max(xseq), max(yseq)
    ratio = my / mx
    W = H / ratio
    fig = plt.figure(figsize=(W, H))
    ax = fig.gca()
    nx.draw(G, pos=pos, node_color='k', node_size=20)
    if label:
        labels = {n: "[{}]".format(n) for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels)
    plt.tight_layout()
    plt.savefig(fpath)
    plt.close()