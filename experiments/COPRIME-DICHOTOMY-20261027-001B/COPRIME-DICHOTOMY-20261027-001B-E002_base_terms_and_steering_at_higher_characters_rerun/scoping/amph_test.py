"""scoping: local four-way form (x at char e, y, w at -e, t = [[x,y],w] at -e) on knots at slope d/p, at every (p, d, e)
where the knot has one-dimensional H1 at zeta^(+-e): amphichiral 3-braid knots versus others"""
import sys
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cd")
from lmc import LieAlgC, CyclicBraidModel

def fourway(p, d, zeta, e=1):
    return LieAlgC(p, d, zeta, "x y w z u t".split(), [1, 1, 1, 2, 2, 3], [e, -e, -e, 0, 0, -e],
                   {("x", "y"): {"z": 1}, ("w", "x"): {"u": 1}, ("w", "z"): {"t": 1}, ("y", "u"): {"t": -1}})

AMPH = {"4_1": ([1, -2, 1, -2], 3), "6_3": ([1, 1, -2, 1, -2, -2], 3), "8_9": ([1, 1, 1, -2, 1, -2, -2, -2], 3),
        "8_17": ([1, 1, -2, 1, -2, 1, -2, -2], 3), "8_18": ([1, -2] * 4, 3), "10_17": ([1] * 4 + [-2, 1] + [-2] * 4, 3)}
CHIR = {"3_1": ([1, 1, 1], 2), "5_2": ([1, 1, 1, 2, -1, 2], 3), "6_1": ([1, 1, 2, -1, -3, 2, -3], 4), "5_1": ([1] * 5, 2),
        "7_1": ([1] * 7, 2), "6_2": ([1, 1, 1, -2, 1, -2], 3), "7_3": ([1] * 5 + [2, -1, 2], 3), "7_5": ([1] * 4 + [2, -1, 2, 2], 3),
        "8_2": ([1] * 5 + [-2, 1, -2], 3), "8_5": ([1, 1, 1, -2, 1, 1, 1, -2], 3), "8_7": ([1] * 4 + [-2, 1, -2, -2], 3)}
PRIMES = [5, 7, 11, 13, 17, 19]
rng = np.random.default_rng(3)
def prim(p):
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in range(2, p) if (p - 1) % q == 0 and all(q % s for s in range(2, q))):
            return g
rows = []
for kind, table in (("amphichiral", AMPH), ("chiral", CHIR)):
    for name, (w, n) in table.items():
        for p in PRIMES:
            g = prim(p)
            for d in range(3, p):
                if (p - 1) % d: continue
                zeta = pow(g, (p - 1) // d, p)
                for e in range(1, d):
                    if np.gcd(e, d) != 1 and False: pass
                    if 2 * e % d == 0: continue
                    L = fourway(p, d, zeta, e)
                    Mo = CyclicBraidModel(w, n, L, p)
                    de, dm = len(Mo.cocycles[e % d]), len(Mo.cocycles[(-e) % d])
                    if de != 2 or dm != 2: continue
                    ix, iy, iw = (L.idx[s] for s in "xyw")
                    bs = 40
                    def rc(c): return (rng.integers(0, p, (bs, 2)) @ Mo.cocycles[c]) % p
                    ok, _, _ = Mo.solve({ix: rc(e % d), iy: rc((-e) % d), iw: rc((-e) % d)})
                    rows.append((kind, name, p, d, e, ok.mean()))
                    print(f"{kind:12s} {name:6s} p={p:2d} d={d:2d} e={e:2d} root t={pow(zeta, e, p):2d}: lift fraction {ok.mean():.2f}", flush=True)
print("amphichiral all vanish:", all(r[5] == 1.0 for r in rows if r[0] == "amphichiral"),
      "| chiral vanishing:", sum(r[5] == 1.0 for r in rows if r[0] == "chiral"), "of", sum(r[0] == "chiral" for r in rows))
