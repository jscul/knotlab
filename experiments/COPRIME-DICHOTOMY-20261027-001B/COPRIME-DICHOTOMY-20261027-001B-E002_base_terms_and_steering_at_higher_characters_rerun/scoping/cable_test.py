"""scoping: local four-way form on (2,1)-cables of knots at roots t with t^2 a root of the companion: amphichiral companions
versus chiral ones; non-square t included"""
import sys
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cdA")
from cd_lib import GLie, BraidAlg, CyclicBraidModel, root_of_unity

def fourway(p, d, zeta, e):
    L = GLie.from_brackets(p, d, "x y w z u t".split(), [1, 1, 1, 2, 2, 3], [e, -e, -e, 0, 0, -e],
                           {("x", "y"): {"z": 1}, ("w", "x"): {"u": 1}, ("w", "z"): {"t": 1}, ("y", "u"): {"t": -1}})
    return BraidAlg(L, zeta)

def cable21(word, n):
    """(2,1)-cable of the closure of word on n strands (bundle i = strands 2i, 2i+1, 0-based)"""
    out = []
    for g in word:
        i = abs(g) - 1                      # bundles i, i+1 -> strands 2i .. 2i+3; 1-based letters 2i+1 .. 2i+3
        a = 2 * i + 1
        fat = [a + 1, a, a + 2, a + 1]
        out += fat if g > 0 else [-x for x in reversed(fat)]
    w = sum(1 if g > 0 else -1 for g in word)
    k = 1 - 2 * w
    out += [1] * k if k > 0 else [-1] * (-k)
    return out, 2 * n

AMPH = {"4_1": ([1, -2, 1, -2], 3), "6_3": ([1, 1, -2, 1, -2, -2], 3), "8_9": ([1, 1, 1, -2, 1, -2, -2, -2], 3)}
CHIR = {"3_1": ([1, 1, 1], 2), "5_2": ([1, 1, 1, 2, -1, 2], 3), "6_1": ([1, 1, 2, -1, -3, 2, -3], 4), "7_5": ([1] * 4 + [2, -1, 2, 2], 3)}
rng = np.random.default_rng(9)
for kind, tab in (("amphichiral", AMPH), ("chiral", CHIR)):
    for name, (w, n) in tab.items():
        cw, cn = cable21(w, n)
        for p in (7, 11, 13, 17, 19):
            for d in range(3, p):
                if (p - 1) % d: continue
                zeta = root_of_unity(p, d)
                for e in range(1, d):
                    if np.gcd(e, d) != 1: continue
                    t = pow(zeta, e, p)
                    A = fourway(p, d, zeta, e)
                    Mo = CyclicBraidModel(cw, cn, A, p)
                    if len(Mo.cocycles[e % d]) != 2 or len(Mo.cocycles[(-e) % d]) != 2: continue
                    ix, iy, iw = (A.idx[s] for s in "xyw")
                    bs = 24
                    def rc(c): return (rng.integers(0, p, (bs, 2)) @ Mo.cocycles[c]) % p
                    ok, _, _ = Mo.solve({ix: rc(e % d), iy: rc((-e) % d), iw: rc((-e) % d)})
                    sq = pow(t, (p - 1) // 2, p) == 1
                    print(f"{kind:11s} cable of {name}: p={p} d={d} t={t} (square={sq}), t^2={t * t % p}: lift fraction {ok.mean():.2f}",
                          flush=True)
