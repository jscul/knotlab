"""Float version of blocks2.series for long horizons (numpy)."""
import itertools
from collections import defaultdict
import numpy as np
def series_f(nv, blocks, N):
    at = defaultdict(list)
    for i, B in enumerate(blocks):
        for z in B: at[z].append(i)
    def mul(a, b): return np.convolve(a, b)[:N + 1]
    one = np.zeros(N + 1); one[0] = 1
    def shift(a): return np.concatenate([[0.0], a[:N]])
    U = {(i, z): np.zeros(N + 1) for i, B in enumerate(blocks) for z in B}
    def phi(i, z, U):
        r = one.copy()
        for w in blocks[i]:
            if w != z: r = mul(r, one + U[(i, w)])
        return r
    for it in range(N + 1):
        new = {}
        for (i, z) in U:
            r = one.copy()
            for j in at[z]:
                if j != i: r = mul(r, phi(j, z, U))
            new[(i, z)] = shift(r)
        U = new
    C = np.zeros(N + 1)
    for x in range(nv):
        r = one.copy()
        for i in at[x]: r = mul(r, phi(i, x, U))
        C = C + shift(r)
    for i, B in enumerate(blocks):
        for m in range(2, len(B) + 1):
            for S in itertools.combinations(B, m):
                pr = one.copy()
                for v in S: pr = mul(pr, U[(i, v)])
                C = C - (m - 1) * pr
    return C[1:]
if __name__ == '__main__':
    import joinlib_path  # noqa
    import joinlib as J
    from blocks2 import blocks_of
    R = J.ring_edges(5)
    for name, n, e in [('5-5', 10, R + J.ring_edges(5, 5) + [(0, 5)]), ('7-7', 14, J.ring_edges(7) + J.ring_edges(7, 7) + [(0, 7)])]:
        nv, B = blocks_of(n, e)
        c = series_f(nv, B, 220)
        for t in (20, 50, 100, 150, 200):
            r = c[t] / c[t - 1]
            print(name, t, 'ratio', round(r, 6), 'a=-3/2', round(r * (t / (t - 1)) ** 1.5, 6), 'a=-5/2', round(r * (t / (t - 1)) ** 2.5, 6))
