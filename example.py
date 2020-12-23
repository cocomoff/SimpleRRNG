import numpy as np
from rrng.generator import generate
from rrng.visualizer import visualize
from rrng.util import clean_up, write_to_csv

if __name__ == '__main__':
    np.random.seed(20201222)
    Dx, Dy = 50, 50
    N = 30
    coeff = 1.3
    G, pos = generate(Dx, Dy, N, coeff)
    G, pos = clean_up(G)
    visualize(G, pos, name="example.png", dir="./output", label=False)
    write_to_csv(G, pos)
