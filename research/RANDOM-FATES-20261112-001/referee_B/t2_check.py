"""Independent referee check of T2 (bandwidth <= 3, i.e. every edge within four consecutive vertices).

(a) the greedy step: every colouring of the three previous vertices and every set of edges {a, b, i} with a, b among them
    leaves a colour for i (64 cases);
(b) the complete band hypergraph (all triples within four consecutive) on n vertices is 2-colourable, n <= 22
    (so every sub-hypergraph is, by monotonicity), and the periodic colouring 0011 0011 ... is proper;
(c) the extension statement exhaustively over ALL edge subsets for n = 8, 9, 10: for each k, every proper colouring of
    [0, k) (for the edges inside [0, k)) extends to a proper colouring of [0, n).
"""
import itertools
import sys

import numpy as np


def band(n, w):
    return [t for t in itertools.combinations(range(n), 3) if t[2] - t[0] <= w - 1]


def kills(n, edges):
    s = np.arange(1 << n, dtype=np.int64)
    K = np.zeros((len(edges), 1 << n), dtype=np.int32)
    for i, e in enumerate(edges):
        m = sum(1 << v for v in e)
        x = s & m
        K[i] = ((x == 0) | (x == m)).astype(np.int32)
    return K


def part_a():
    bad = 0
    for col in itertools.product((0, 1), repeat=3):
        for sub in range(8):
            prs = [p for j, p in enumerate(itertools.combinations(range(3), 2)) if sub >> j & 1]
            okc = [c for c in (0, 1) if not any(col[a] == c and col[b] == c for a, b in prs)]
            if not okc:
                bad += 1
    return bad


def part_b(nmax):
    res = {}
    for n in range(3, nmax + 1):
        E = band(n, 4)
        per = [(i // 2) % 2 for i in range(n)]
        per_ok = all(len({per[v] for v in e}) == 2 for e in E)
        if n <= 22:
            s = np.arange(1 << n, dtype=np.int64)
            ok = np.ones(1 << n, dtype=bool)
            for e in E:
                m = sum(1 << v for v in e)
                x = s & m
                ok &= (x != 0) & (x != m)
            cnt = int(ok.sum())
        res[n] = (len(E), per_ok, cnt)
    return res


def part_c(n, chunk=1 << 14):
    E = band(n, 4)
    m = len(E)
    K = kills(n, E)
    Kk = {}
    Ek = {}
    for k in range(3, n):
        idx = [i for i, e in enumerate(E) if e[2] < k]
        Ek[k] = idx
        Kk[k] = kills(k, [E[i] for i in idx]) if idx else None
    failures = 0
    total = 1 << m
    for start in range(0, total, chunk):
        subs = np.arange(start, min(total, start + chunk), dtype=np.int64)
        bits = ((subs[:, None] >> np.arange(m)) & 1).astype(np.int32)
        ok = (bits @ K) == 0  # proper colourings of [0, n)
        if not ok.any(axis=1).all():
            failures += int((~ok.any(axis=1)).sum())
        for k in range(3, n):
            if Kk[k] is None:
                continue
            okk = (bits[:, Ek[k]] @ Kk[k]) == 0
            proj = ok.reshape(len(subs), 1 << (n - k), 1 << k).any(axis=1)
            failures += int((proj != okk).any(axis=1).sum())
    return total, failures


if __name__ == "__main__":
    print("greedy-step failures (of 64 cases):", part_a())
    for n, v in part_b(22).items():
        print("n", n, "band-3 edges", v[0], "periodic 0011 proper", v[1], "proper colourings of complete band", v[2])
    for n in [int(x) for x in sys.argv[1:]]:
        print("extension, all subsets, n", n, part_c(n), flush=True)
