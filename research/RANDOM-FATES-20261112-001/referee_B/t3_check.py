"""Independent referee check of T3 and of K3's minimum (10 knots) for edges within five consecutive vertices.

(1) K5^(3) has no proper 2-colouring.
(2) brute force (DFS over edge subsets in index order with incremental OR of the colourings each edge kills):
    no set of <= 9 band-4 triples (within five consecutive) on n vertices is non-2-colourable; count the 10-sets that are.
(3) exact minimum by MILP (scipy/HiGHS), a different method from check.py's RC2 MaxSAT, for n = 5..14.
"""
import itertools
import sys

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds


def band(n, w):
    return [t for t in itertools.combinations(range(n), 3) if t[2] - t[0] <= w - 1]


def killmasks(n, E):
    # colourings with vertex 0 coloured 0 (complement symmetry): s in [0, 2^n) with bit 0 = 0
    cols = [s for s in range(1 << n) if not s & 1]
    km = []
    for e in E:
        m = 0
        for j, s in enumerate(cols):
            vals = {(s >> v) & 1 for v in e}
            if len(vals) == 1:
                m |= 1 << j
        km.append(m)
    return cols, km


def brute(n, kmax):
    E = band(n, 5)
    cols, km = killmasks(n, E)
    full = (1 << len(cols)) - 1
    found = {k: 0 for k in range(1, kmax + 1)}
    m = len(E)

    def dfs(start, depth, acc):
        for i in range(start, m):
            a = acc | km[i]
            if a == full:
                found[depth + 1] += 1
                # supersets in this branch are not minimal; still count only this one
                continue
            if depth + 1 < kmax:
                dfs(i + 1, depth + 1, a)
    dfs(0, 0, 0)
    return len(E), found


def milp_min(n):
    E = band(n, 5)
    cols, km = killmasks(n, E)
    A = np.zeros((len(cols), len(E)))
    for i, mk in enumerate(km):
        for j in range(len(cols)):
            if mk >> j & 1:
                A[j, i] = 1
    res = milp(c=np.ones(len(E)), constraints=LinearConstraint(A, lb=np.ones(len(cols)), ub=np.inf),
               integrality=np.ones(len(E)), bounds=Bounds(0, 1))
    chosen = [E[i] for i in range(len(E)) if res.x[i] > 0.5]
    return len(E), res.status, round(res.fun), chosen


def two_colourable(n, E):
    for s in range(1 << n):
        if all(len({(s >> v) & 1 for v in e}) == 2 for e in E):
            return True
    return False


if __name__ == "__main__":
    print("K5^(3) 2-colourable:", two_colourable(5, list(itertools.combinations(range(5), 3))))
    ex = {6: [[0, 1, 2], [0, 3, 4], [1, 2, 3], [1, 2, 4], [1, 3, 4], [1, 3, 5], [1, 4, 5], [2, 3, 4], [2, 3, 5], [2, 4, 5]],
          7: [[0, 1, 3], [0, 2, 4], [1, 2, 3], [1, 2, 4], [1, 4, 5], [2, 3, 4], [2, 3, 5], [2, 5, 6], [3, 4, 5], [3, 4, 6]],
          8: [[0, 1, 3], [0, 2, 4], [1, 2, 4], [1, 2, 5], [1, 3, 4], [2, 3, 4], [2, 3, 5], [2, 3, 6], [3, 4, 5], [4, 5, 6]]}
    for n, E in ex.items():
        print("check.py example n", n, "within five consecutive", all(e[2] - e[0] <= 4 for e in E),
              "2-colourable", two_colourable(n, E), "edges", len(E), "distinct", len({tuple(e) for e in E}))
    mode = sys.argv[1]
    if mode == "milp":
        for n in range(5, int(sys.argv[2]) + 1):
            print("MILP n", n, milp_min(n), flush=True)
    else:
        for n in [int(x) for x in sys.argv[2:]]:
            print("brute n", n, brute(n, 10), flush=True)
