"""scoping: layered obstruction model for a knot group presentation plus the relator x_1^d (the closed manifold S^3_(d/p)(K):
lambda^p acts trivially, so only mu^d remains); generators are meridians labelled in the coset N sigma"""
import sys
import numpy as np
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/6694d27d-4771-575f-adbb-a5c8aaccce97/scratchpad/cdA")
from cd_lib import GLie, BraidAlg, Grp, nullspace, solve_any

def two_bridge(alpha, beta):
    """Schubert presentation <a, b | a w = w b>, w = b^e1 a^e2 b^e3 ... (alpha - 1 letters), e_i = (-1)^floor(i beta / alpha)"""
    alpha = abs(alpha)
    beta = beta % alpha
    if beta % 2 == 0: beta -= alpha          # Schubert's normal form needs an odd representative (same knot)
    eps = [1 - 2 * (((i * beta) // alpha) % 2) for i in range(1, alpha)]
    w = [(2 if i % 2 == 0 else 1) * e for i, e in enumerate(eps)]       # letters alternate b, a, b, ...
    inv = lambda u: [-g for g in reversed(u)]
    return 2, [[1] + w + [-2] + inv(w)]

class PresModel:
    def __init__(self, ngen, rels, A):
        self.n, self.rels, self.A, self.p = ngen, rels + [[1] * A.d], A, A.p
        self.Lin = {c: self._linear_part(c) for c in range(A.d)}
        self.cocycles = {c: nullspace(self.Lin[c], self.p) for c in range(A.d)}

    def run(self, V, A=None):
        A = A or self.A
        G = Grp(A)
        gens = [(V[:, q].copy(), 1) for q in range(self.n)]
        out = np.zeros((V.shape[0], len(self.rels), A.D), dtype=np.int64)
        for r, rel in enumerate(self.rels):
            acc = (np.zeros_like(V[:, 0]), 0)
            for g in rel:
                acc = G.mul(acc, gens[abs(g) - 1] if g > 0 else G.inv(gens[abs(g) - 1]))
            assert acc[1] == 0
            out[:, r] = acc[0]
        return out

    def _linear_part(self, c):
        L1 = GLie(self.p, self.A.d, ["e"], [1], [c], np.zeros((1, 1, 1), dtype=np.int64), check=False)
        A1 = BraidAlg(L1, self.A.zeta)
        V = np.zeros((self.n, self.n, 1), dtype=np.int64)
        for q in range(self.n): V[q, q, 0] = 1
        return self.run(V, A1)[:, :, 0].T % self.p

    def solve(self, inputs):
        A, p = self.A, self.p
        bs = next(iter(inputs.values())).shape[0]
        V = np.zeros((bs, self.n, A.D), dtype=np.int64)
        ok = np.ones(bs, dtype=bool)
        for lay in range(1, int(A.layer.max()) + 1):
            R = self.run(V)
            for k in [k for k in range(A.D) if A.layer[k] == lay]:
                X, bad = solve_any(self.Lin[int(A.chars[k])], (-R[:, :, k]).T % p, p)
                if A.chars[k] == 0: assert not bad.any()
                ok &= ~bad
                V[:, :, k] = (X.T + (inputs[k] if k in inputs else 0)) % p
        return ok, V
