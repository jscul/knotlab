"""f(d) per support pattern of d = (C0, A0, B0, S0); checks Galois-invariance on random scalings"""
import sys, itertools, random
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/bc")
import mlib
p = int(sys.argv[1])
mu = mlib.milnor(mlib.P4, 4, p)
w = np.exp(2j * np.pi * np.arange(p) / p)
CA = np.array(list(itertools.product(range(p), repeat=6)), dtype=np.int64)
Bs = np.array(list(itertools.product(range(p), repeat=3)), dtype=np.int64)
def f(d):
    tot = np.zeros(p)
    for b in Bs:
        C = [np.full(len(CA), d[0])] + [CA[:, k] for k in range(3)]
        A = [np.full(len(CA), d[1])] + [CA[:, 3 + k] for k in range(3)]
        Bv = [d[2]] + list(b)
        Phi = [np.zeros(len(CA), dtype=np.int64) for _ in range(4)]
        for (i1, i2, i3, j), v in mu.items():
            Phi[j] = (Phi[j] + v * C[i1] * A[i2] * Bv[i3]) % p
        mask = (Phi[1] == 0) & (Phi[2] == 0) & (Phi[3] == 0)
        tot += np.bincount((d[3] * Phi[0][mask]) % p, minlength=p)
    val = p ** 3 * np.dot(tot, w)
    assert abs(val.imag) < 1e-3
    return round(val.real)
rng = random.Random(0)
for pat in itertools.product((0, 1), repeat=4):
    v = f(pat)
    checks = [f(tuple(x * rng.randrange(1, p) for x in pat)) for _ in range(2)]
    print("pattern (C0,A0,B0,S0) =", pat, "f =", v, "= p^6 *", v / p ** 6, "random rescalings:", checks, flush=True)
