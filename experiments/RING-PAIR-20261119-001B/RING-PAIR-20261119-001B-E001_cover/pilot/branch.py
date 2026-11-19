"""Radius of convergence rho of the cover model's system (positive polynomial system U = y * prod Phi): the largest y for which the
fixed-point iteration from 0 stays bounded.  Rate lambda = 1/rho."""
from collections import defaultdict
import numpy as np
def make_sys(blocks):
    at = defaultdict(list)
    for i, B in enumerate(blocks):
        for z in B: at[z].append(i)
    keys = [(i, z) for i, B in enumerate(blocks) for z in B]
    idx = {k: n for n, k in enumerate(keys)}
    def step(u, y):
        out = np.empty_like(u)
        for (i, z), n in idx.items():
            r = 1.0
            for j in at[z]:
                if j != i:
                    for w in blocks[j]:
                        if w != z: r *= 1.0 + u[idx[(j, w)]]
            out[n] = y * r
        return out
    return keys, step
def bounded(step, m, y, iters=20000):
    u = np.zeros(m)
    for k in range(iters):
        v = step(u, y)
        if not np.all(np.isfinite(v)) or v.max() > 1e8: return False
        if np.max(np.abs(v - u)) < 1e-13: return True
        u = v
    return True
def rho(blocks):
    keys, step = make_sys(blocks)
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if bounded(step, len(keys), mid): lo = mid
        else: hi = mid
    return lo
if __name__ == '__main__':
    import sys
    import joinlib_path  # noqa
    import joinlib as J, job
    from blocks2 import blocks_of
    cs = dict(job.cases())
    for cid in sys.argv[1:]:
        p = cs[cid]
        nv, B = blocks_of(p['n'], [tuple(e) for e in p['edges']], [int(k) for k, v in p['surplus'].items() for _ in range(v)])
        r = rho(B)
        print(cid, 'rho', r, 'lambda', 1 / r)
