"""Clean-edge conditions modulo gamma_4 for a class-4 algebra and an edge (a, b): which of (K), (B0), (B1'), (B2'), (V3), (V3')
fail.  Helpers are exec'd from the closed ticket A check (read-only)."""
import glob, sys
import numpy as np
import os
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
A = glob.glob(os.path.join(ROOT, "proofs/CLASS4-PAIRS-20261028-001A/*P001_*/check.py"))[0]
src = open(A).read().split("# ---------------------------------------------------------------- 1 the census")[0]
g = {"__file__": A, "__name__": "helpers"}
exec(compile(src, A, "exec"), g)


def conds(chars, d, p, edge):
    L = g["free_graded"](p, d, list(chars), 4)
    M = g["m_ideal"](L, d); G = g["lcs"](L, M, 5); Z = np.zeros((0, L.D), dtype=np.int64)
    K = G[3]
    kchars = {t for t, v in g["char_dims"](L, K, d).items() if v and t % d}
    def mod(R):
        S = g["span_rows"](np.concatenate([R, K]), p) if len(K) else (R if len(R) else None)
        return S if S is not None else Z
    G2 = mod(G[1]); G3 = mod(G[2]) if (len(G[2]) or len(K)) else Z
    lay1 = g["complement_rows"](L, M, G2, p); lay2 = g["complement_rows"](L, G2, G3, p)
    a, b = edge; gg = (a + b) % d
    RR = {i: g["R_of"](t, d) for i, t in enumerate((a, b, gg))}
    L1 = {i: g["char_rows"](L, lay1, d, RR[i]) for i in range(3)}
    L2 = {i: g["char_rows"](L, lay2, d, RR[i]) for i in range(3)}
    bc = g["bracket_chars"]
    pair = bool(bc(L, g["char_rows"](L, lay1, d, [a]), g["char_rows"](L, lay1, d, [b]), G3, d))
    Z1 = g["zero_part"](L, L1[2], L1[0], G3, d); Z2 = g["zero_part"](L, L1[0], L1[1], G3, d)
    v3p = any(np.any(L.br(x[None, :], z[None, :])[0] % p) for (Zr, Lx) in ((Z1, L1[1]), (Z2, L1[2]))
              for c, RA in Lx.items() if c in RR[0] for x in RA for z in Zr)
    fail = {n for n, bad in (("K", bool((RR[0] | RR[1] | RR[2]) & kchars)),
                             ("B0", bool(bc(L, L1[1], L1[2], G3, d))),
                             ("B1'", not bc(L, L1[2], L1[0], G3, d) <= RR[1] | {0}),
                             ("B2'", not bc(L, L1[0], L1[1], G3, d) <= RR[2] | {0}),
                             ("V3", bool(g["v3_chars"](L, L1, L2, G3, Z, d) & RR[0])), ("V3'", v3p)) if bad}
    return {"pair bracket nonzero": pair, "roots": {i: sorted(RR[i]) for i in range(3)}, "gamma_4 chars": sorted(kchars),
            "failing": sorted(fail), "slot-2 layer-1 data": bool(L1[2])}


if __name__ == "__main__":
    for chars, edge in [([1, 1], (1, 1)), ([0, 1, 1], (1, 1)), ([1, 1, 1], (1, 1)), ([1, 2], (1, 2)), ([1, 2], (2, 1)),
                        ([1, 3], (1, 3)), ([1, 3], (3, 1)), ([0, 1, 2], (1, 2)), ([0, 1, 2], (2, 1))]:
        print(chars, edge, conds(chars, 5, 11, edge), flush=True)
