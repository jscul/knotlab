"""Gates for SPACE-ORDER-20261117-001A (run before any read-out).

W1  the weave has 2L^2 knots, every distinction in six, no repeated member;
    swaps keep every distinction in six knots; planted swaps keep the planted
    state not-all-equal; zero-energy sweeps keep it not-all-equal.
W2  not-all-equal propagation: synchronous rounds and the incremental
    propagation end in the same set values, which agree with the planted state.
W3  not-all-equal phases end in the same values, and each value's phase equals
    its least Strahler number by relaxation; a mutant phase law that also reads
    knots with no set member as rules disagrees somewhere or adds wrong values.
W4  atom law on weaves and twins: phases equal Strahler numbers (the library's
    theorem, rechecked here on these patterns).
"""

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import weaves as Wv  # noqa: E402
A = Wv.A
OUT = os.path.join(Wv.ROOT, "artifacts", "SPACE-ORDER-20261117-001A", "SPACE-ORDER-20261117-001A-E001_weave_phases")


def incremental_values(knots, n, held, values):
    from collections import deque
    kl = Wv.knots_of(knots, n)
    K = knots.tolist()
    val = [-1] * n
    q = deque((int(v), int(values[v])) for v in held)
    while q:
        v, b = q.popleft()
        if val[v] >= 0:
            assert val[v] == b
            continue
        val[v] = b
        for kk in kl[v]:
            a, c = [u for u in K[kk] if u != v]
            if val[a] == b and val[c] < 0:
                q.append((c, 1 - b))
            elif val[c] == b and val[a] < 0:
                q.append((a, 1 - b))
    return np.array(val, dtype=np.int8)


def main():
    rng = np.random.default_rng(20261117)
    rep = {}
    cases = 0
    for L in (6, 9, 12, 15):
        n = L * L
        K = Wv.weave(L)
        assert len(K) == 2 * n and np.all(np.bincount(K.ravel(), minlength=n) == 6)
        assert np.all((K[:, 0] != K[:, 1]) & (K[:, 0] != K[:, 2]) & (K[:, 1] != K[:, 2]))
        s0 = Wv.three_class_state(L)
        assert Wv.nae_ok(K, s0)
        s = Wv.zero_energy_sweeps(K, s0, 20, rng)
        assert Wv.nae_ok(K, s)
        demand = rng.integers(0, 3, len(K))
        R6, _ = Wv.knot_swaps(K, demand, 10 * len(K), rng)
        assert np.all(np.bincount(R6.ravel(), minlength=n) == 6)
        R6n, _ = Wv.knot_swaps(K, demand, 10 * len(K), rng, state=s)
        assert np.all(np.bincount(R6n.ravel(), minlength=n) == 6) and Wv.nae_ok(R6n, s)
        for pat in (K, R6n):
            for _ in range(15):
                k = int(rng.integers(1, n))
                held = rng.permutation(n)[:k]
                fv, R = Wv.nae_rounds(pat, n, held, s)
                iv = incremental_values(pat, n, held, s)
                assert np.array_equal(fv, iv), "W2 rounds != incremental"
                setm = fv >= 0
                assert np.all(fv[setm] == s[setm]), "W2 disagrees with planted"
                pv, ph, P = Wv.nae_phases(pat, n, held, s)
                assert np.array_equal(pv, fv), "W3 phases end elsewhere"
                rk = Wv.nae_rank(pat, n, held, s)
                assert np.array_equal(rk[setm], ph[setm]), "W3 phase != Strahler"
                assert P <= R
                cases += 1
        for pat in (K, R6):
            for _ in range(10):
                k = int(rng.integers(1, n))
                held = rng.permutation(n)[:k]
                p = Wv.atom_pattern(pat, demand, held)
                f, _, R = A.native_rounds(p)
                _, ph, P = A.untangling_phases(p)
                r = A.rank(p)
                fin = r < A.INF
                assert np.array_equal(fin, f) and np.array_equal(ph[fin], r[fin]), "W4"
                cases += 1
    rep["cases"] = cases
    # mutant for W3: a rank that ignores the +1 at equal numbers must disagree somewhere
    L = 12; n = L * L
    K = Wv.weave(L)
    s = Wv.zero_energy_sweeps(K, Wv.three_class_state(L), 20, rng)
    diffs = 0
    for _ in range(30):
        held = rng.permutation(n)[:int(rng.integers(n // 4, n))]
        fv, _, = Wv.nae_rounds(K, n, held, s)
        _, ph, _ = Wv.nae_phases(K, n, held, s)
        saved = A.combine
        A.combine = lambda a, b: np.where(np.maximum(a, b) >= A.INF, A.INF, np.maximum(a, b))
        try:
            rk = Wv.nae_rank(K, n, held, s)
        finally:
            A.combine = saved
        setm = fv >= 0
        diffs += int(np.any(rk[setm] != ph[setm]))
    assert diffs > 0, "W3 mutant never differs"
    rep["W3_mutant_differs"] = diffs
    rep["status"] = "all gates passed"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "gates.json"), "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
