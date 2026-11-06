"""Two-parameter version: recover the number of proper 3-colourings P(Gamma, 3) itself.

L(j, k) = L_Gamma with j trefoils tied into every component, then every edge component
replaced by k parallel 0-framed copies.  Then
   H(L(j,k)) = sum_s 3^{j s} B_s(k),   B_0(k) = 3^{m k} Z(Gamma; 3, 2^{k-1}),
so j = 0..n+m gives B_0(k), and k = 1..m+1 gives the degree-m polynomial y -> Z(Gamma; 3, y),
whose value at y = 0 is P(Gamma, 3).  All H values are computed directly on the links.
"""
import sys, time
from fractions import Fraction
sys.path.insert(0, '.')
from braidlab import *
from test_surgery import solve
from potts_reduction import L_gamma, count_psi_parallel, potts


def build_Ljk(n, edges, j, k):
    w, N = L_gamma(n, edges)
    c = n + len(edges)
    w, N, reps = tie_trefoils(w, N, list(range(c)), j)
    comps = components(w, N)
    rep_comp = [next(t for t, cc in enumerate(comps) if r in cc) for r in reps]
    ncopies = [1] * len(comps)
    for idx in range(len(edges)):
        ncopies[rep_comp[n + idx]] = k
    return cable(w, N, ncopies, [0] * len(comps))


def lagrange_at_zero(xs, ys):
    tot = Fraction(0)
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        term = Fraction(yi)
        for jx, xj in enumerate(xs):
            if jx != i:
                term *= Fraction(0 - xj, xi - xj)
        tot += term
    return tot


if __name__ == '__main__':
    graphs = {'P3 (path)': (3, [(0, 1), (1, 2)]), 'K3 (triangle)': (3, [(0, 1), (1, 2), (0, 2)])}
    for name in (sys.argv[1:] or list(graphs)):
        n, edges = graphs[name]
        m, c = len(edges), n + len(edges)
        t0 = time.time()
        ys, Zs = [], []
        for k in range(1, m + 2):
            Hs = []
            for j in range(c + 1):
                cw, cn = build_Ljk(n, edges, j, k)
                Hs.append(count_psi_parallel(cw, cn))
            B = solve([3 ** s for s in range(c + 1)], Hs)
            y = 2 ** (k - 1)
            Zk = B[0] / Fraction(3) ** (m * k)
            ys.append(y)
            Zs.append(Zk)
            print(f'  {name}: k={k} (y={y}) B_0={B[0]}  Z from links={Zk}  Z direct={potts(n, edges, 3, y)}', flush=True)
        P3 = lagrange_at_zero(ys, Zs)
        direct = potts(n, edges, 3, 0)
        print(f'{name}: P(Gamma,3) recovered from link counts = {P3}, direct = {direct}',
              'OK' if P3 == direct else 'FAIL', f'({time.time() - t0:.0f}s)', flush=True)
