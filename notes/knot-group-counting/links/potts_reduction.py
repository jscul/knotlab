"""End-to-end check of the reduction  Potts(q=3) on a graph  ->  H_L(S3) on links.

Construction for a graph Gamma = (V, E), n = |V|, m = |E|:
  L_Gamma : n 'vertex' components U_v and m 'edge' components K_e, realised as the
            closure of the pure braid prod_{e=uv} A_{u,e} A_{v,e}^{-1}; only the linking
            numbers matter: lk(K_e, U_u) = +1, lk(K_e, U_v) = -1, all others 0.
  L(j)    : tie j trefoils into every component of L_Gamma, then replace every edge
            component by 2 parallel copies (0-framed).
Claim:  H(L(j)) = sum_{s=0}^{n+m} 3^{j s} B_s  with
        B_0 = sum over rho: pi -> A3 of prod_e |C(rho(lambda_e))| = 9^m Z(Gamma; q=3, y=2),
where Z(Gamma; q, y) = sum_{sigma: V -> [q]} y^{#monochromatic edges}.
So B_0 is obtained from the n+m+1 numbers H(L(0)), ..., H(L(n+m)) by a Vandermonde solve,
and Z(Gamma; 3, 2) = T-polynomial point (4, 2) up to a trivial factor, #P-hard (JVW 1990).
H(L(j)) is computed DIRECTLY from the braid of L(j) (sector method, exact).
"""
import sys, itertools, time
from fractions import Fraction
from multiprocessing import Pool
sys.path.insert(0, '.')
from braidlab import *
from test_surgery import solve


def L_gamma(n, edges):
    word = []
    N = n + len(edges)
    for idx, (u, v) in enumerate(edges):
        e = n + idx
        word += A_gen(u, e)
        word += [-x for x in reversed(A_gen(v, e))]
    return word, N


_W = None


def _init(word, n, ci):
    global _W
    _W = (word, n, ci)


def _sector(psi):
    word, n, ci = _W
    return sector_count(word, n, [psi[ci[p]] for p in range(n)])


def count_psi_parallel(word, n, procs=24):
    comps, ci = comp_index(word, n)
    pats = list(itertools.product((0, 1), repeat=len(comps)))
    with Pool(procs, initializer=_init, initargs=(word, n, ci)) as pool:
        vals = pool.map(_sector, pats, chunksize=max(1, len(pats) // (4 * procs)))
    return sum(vals)


def build_Lj(n, edges, j):
    w, N = L_gamma(n, edges)
    c = n + len(edges)
    w, N, reps = tie_trefoils(w, N, list(range(c)), j)
    comps = components(w, N)
    rep_comp = [next(k for k, cc in enumerate(comps) if r in cc) for r in reps]
    ncopies = [1] * len(comps)
    for idx in range(len(edges)):
        ncopies[rep_comp[n + idx]] = 2
    cw, cn = cable(w, N, ncopies, [0] * len(comps))
    return cw, cn


def potts(n, edges, q, y):
    return sum(y ** sum(1 for u, v in edges if s[u] == s[v]) for s in itertools.product(range(q), repeat=n))


def sectors_from_formula(n, edges):
    """B_s = sum over rho in Hom(pi_{L_Gamma}, S3) with s transposition meridians of
    prod_e |C(rho(lambda_e))|  (brute force on L_Gamma itself, for cross-checking)."""
    w, N = L_gamma(n, edges)
    from test_cable import seifert_long
    comps = components(w, N)
    B = {}
    for fp in fixed_points(w, N):
        labels = [ELTS[x] for x in fp]
        sl = seifert_long(w, N, labels, 1)
        s = sum(m[1] for m, lam in sl)
        wt = 1
        for k, cc in enumerate(comps):
            if cc[0] >= n:  # edge component (pure braid: one strand each)
                wt *= CENT[sl[k][1]]
        B[s] = B.get(s, 0) + wt
    return B


if __name__ == '__main__':
    graphs = {
        'K2 (one edge)': (2, [(0, 1)]),
        'P3 (path)': (3, [(0, 1), (1, 2)]),
        'K3 (triangle)': (3, [(0, 1), (1, 2), (0, 2)]),
        'K3 with a doubled edge': (3, [(0, 1), (1, 2), (0, 2), (0, 2)]),
        'C4 (square)': (4, [(0, 1), (1, 2), (2, 3), (0, 3)]),
    }
    which = sys.argv[1:] or list(graphs)
    for name in which:
        n, edges = graphs[name]
        m = len(edges)
        c = n + m
        t0 = time.time()
        Hs = []
        for j in range(c + 1):
            cw, cn = build_Lj(n, edges, j)
            Hs.append(count_psi_parallel(cw, cn))
            print(f'  {name}: j={j} strands={cn} crossings={len(cw)} components={len(components(cw, cn))} H={Hs[-1]}', flush=True)
        B = solve([3 ** s for s in range(c + 1)], Hs)
        Z = potts(n, edges, 3, 2)
        target = 9 ** m * Z
        line = f'{name}: B_0 (from link counts) = {B[0]}   9^m Z(Gamma;3,2) = {target}   Z = {Z}'
        if c <= 7:
            Bf = sectors_from_formula(n, edges)
            line += f'   sector cross-check {"OK" if all(B[s] == Bf.get(s, 0) for s in range(c + 1)) else "FAIL"}'
        print(line, 'OK' if B[0] == target else 'FAIL', f'({time.time() - t0:.0f}s)', flush=True)
