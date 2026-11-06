"""edge weight f(d) = sum over private leaf values of omega^T(d, privates), leaf 0 = vertex difference, leaves 1..3 private"""
import sys, itertools, cmath
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/bc")
import mlib
p = int(sys.argv[1]) if len(sys.argv) > 1 else 5
mu = mlib.milnor(mlib.P4, 4, p)
print("mu:", mu)
# T(c,a,b,s) = sum mu(i1,i2,i3,j) C_i1 A_i2 B_i3 S_j ; Phi_j = coefficient of S_j
G = np.array(list(itertools.product(range(p), repeat=9)), dtype=np.int64)   # (C1..3, A1..3, B1..3)
def leafvals(G, d):
    C = [np.full(len(G), d[0])] + [G[:, k] for k in range(3)]
    A = [np.full(len(G), d[1])] + [G[:, 3 + k] for k in range(3)]
    B = [np.full(len(G), d[2])] + [G[:, 6 + k] for k in range(3)]
    return C, A, B
f = {}
w = np.exp(2j * np.pi * np.arange(p) / p)
for d in itertools.product(range(p), repeat=4):
    C, A, B = leafvals(G, d)
    Phi = [np.zeros(len(G), dtype=np.int64) for _ in range(4)]
    for (i1, i2, i3, j), v in mu.items():
        Phi[j] = (Phi[j] + v * C[i1] * A[i2] * B[i3]) % p
    mask = (Phi[1] == 0) & (Phi[2] == 0) & (Phi[3] == 0)
    vals = (d[3] * Phi[0][mask]) % p
    cnt = np.bincount(vals, minlength=p)
    f[d] = p ** 3 * complex(np.dot(cnt, w))
re = {d: round(v.real, 6) for d, v in f.items()}
assert all(abs(v.imag) < 1e-6 for v in f.values())
vals = sorted(set(re.values()))
print("p", p, "distinct values of f:", vals)
print("min", min(vals), "f(0) =", re[(0, 0, 0, 0)])
neg = [d for d, v in re.items() if v < -1e-9]
print("negative entries:", len(neg), neg[:10])
from collections import Counter
print(Counter(re.values()))
