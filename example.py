import numpy as np
from rrng.generator import generate
from rrng.visualizer import visualize
from rrng.util import clean_up

if __name__ == '__main__':
    np.random.seed(20201222)
    Dx, Dy = 200, 200
    N = 30
    coeff = 1.2
    G, pos = generate(Dx, Dy, N, coeff)
    G, pos = clean_up(G)
    visualize(G, pos, name="example.png", dir="./output")
