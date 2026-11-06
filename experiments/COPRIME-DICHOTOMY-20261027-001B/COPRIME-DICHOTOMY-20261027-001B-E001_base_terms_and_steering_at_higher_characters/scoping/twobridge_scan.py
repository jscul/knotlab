import sys
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cd")
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cdA")
from presmodel import PresModel, two_bridge
from cd_lib import GLie, BraidAlg, root_of_unity

def fourway(p, d, zeta, e):
    L = GLie.from_brackets(p, d, "x y w z u t".split(), [1, 1, 1, 2, 2, 3], [e, -e, -e, 0, 0, -e],
                           {("x", "y"): {"z": 1}, ("w", "x"): {"u": 1}, ("w", "z"): {"t": 1}, ("y", "u"): {"t": -1}})
    return BraidAlg(L, zeta)

rng = np.random.default_rng(5)
# sanity: Alexander roots of known 2-bridge knots via dim of cocycles
for (al, be, name) in [(5, 2, "4_1"), (3, 1, "3_1"), (7, 3, "5_2"), (9, 2, "6_1"), (17, 4, "8_3"), (13, 5, "6_3")]:
    n, rels = two_bridge(al, be)
    p, d = 13, 12
    A = fourway(p, d, root_of_unity(p, d), 1)
    M = PresModel(n, rels, A)
    print(name, {pow(root_of_unity(p, d), c, p): len(M.cocycles[c]) for c in range(1, d) if len(M.cocycles[c]) > 1})
for (p, d, e) in [(7, 6, 1), (11, 10, 1), (13, 4, 1), (5, 4, 1), (7, 3, 1), (13, 3, 1)]:
    zeta = root_of_unity(p, d); t0 = pow(zeta, e, p)
    sq = pow(t0, (p - 1) // 2, p) == 1
    A = fourway(p, d, zeta, e)
    target = t0 * pow((t0 - 1) ** 2 % p, p - 2, p) % p
    res = []
    for Mm in range(-9, 10):
        for Nn in range(-9, 10):
            if Mm == 0 or Nn == 0 or (Mm * Nn) % p != target: continue
            al = 4 * Mm * Nn + 1
            if abs(al) < 3: continue
            n, rels = two_bridge(al, 2 * Nn)
            Mo = PresModel(n, rels, A)
            if len(Mo.cocycles[e % d]) != 2 or len(Mo.cocycles[(-e) % d]) != 2: res.append((Mm, Nn, "dim")); continue
            ix, iy, iw = (A.idx[s] for s in "xyw")
            bs = 30
            def rc(c): return (rng.integers(0, p, (bs, 2)) @ Mo.cocycles[c]) % p
            ok, _ = Mo.solve({ix: rc(e % d), iy: rc((-e) % d), iw: rc((-e) % d)})
            res.append((Mm, Nn, round(float(ok.mean()), 2)))
    print(f"p={p} d={d} t0={t0} square={sq} MN={target}:", res, flush=True)
