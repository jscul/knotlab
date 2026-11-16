"""Gate checks for CARRY-STRANDS-20261116-001A (run before any read-out).

G1  w = 1 is the forcing law: each distinction's phase equals
    SEQUENTIAL-WALL's untangling phase.
G2  for every w, keep and spend-only, the forced set is the closure.
G3  spend-only, phase = ceil(sigma / w) for every forced distinction.
G4  spend-only, the doubling rounds T >= the largest sigma.
G5  keeping and more carried distinctions never add phases.
G6  ladder: two carried distinctions with keeping force the top in one phase;
    spend-only ceil((k + 1) / 2) phases.
G8  the advisor's example for a copying law: x and y at the ends of rule
    chains, atoms (x, y -> c) and (c, x -> t).  Since both laws here may
    derive a distinction again, both reach t in one phase with two carried
    distinctions (sigma(t) = 2); a law that copied instead of re-deriving would
    need three.
G7  mutant: the law with joins switched off equals w = 1, and differs from
    the w = 2 law somewhere.
"""

import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import strands as S  # noqa: E402
A = S.A
ROOT = S.ROOT
OUT = os.path.join(ROOT, "artifacts", "CARRY-STRANDS-20261116-001A", "CARRY-STRANDS-20261116-001A-E001_carried")


def no_join(p, w):
    saved = S._phase_rules

    def rules(p_, f_):
        st, fo, _ = saved(p_, f_)
        return st, fo, {}
    S._phase_rules = rules
    try:
        return S.carried_phases(p, w, keep=True)
    finally:
        S._phase_rules = saved


def main():
    rng = np.random.default_rng(20261116)
    rep = {"cases": 0}
    mut_diff = 0
    for n in range(5, 15):
        for _ in range(40):
            trip = A.random_pattern(n, float(rng.choice([1.0, 1.5, 2.5, 4.0])), rng)
            held = rng.choice(n, int(rng.integers(1, max(2, n // 2))), replace=False)
            p = A.Pattern(n, trip, held)
            f, _, _ = A.native_rounds(p)
            _, ph, P = A.untangling_phases(p)
            sig = A.rank(p)
            fin = sig < A.INF
            r1 = S.carried_phases(p, 1)
            assert np.array_equal(r1["phase"][fin], ph[fin]) and r1["P"] == P, "G1"
            prev = {True: r1["phase"], False: r1["phase"]}
            for w in (1, 2, 3):
                for copies in (False, True):
                    r = S.carried_phases(p, w, keep=copies)
                    assert np.array_equal(r["forced"], f), "G2"
                    if not copies:
                        want = np.ceil(sig[fin] / w).astype(int)
                        assert np.array_equal(r["phase"][fin], want), "G3"
                        assert r["T"] >= (int(sig[fin].max()) if fin.any() else 0), "G4"
                    assert np.all(r["phase"][fin] <= prev[copies][fin]), "G5 w"
                    prev[copies] = r["phase"]
                rc = S.carried_phases(p, w, keep=True)
                rn = S.carried_phases(p, w, keep=False)
                assert np.all(rc["phase"][fin] <= rn["phase"][fin]), "G5 keep"
            m = no_join(p, 2)
            assert np.array_equal(m["phase"][fin], r1["phase"][fin]), "G7 equal"
            mut_diff += int(not np.array_equal(S.carried_phases(p, 2)["phase"][fin], r1["phase"][fin]))
            rep["cases"] += 1
    assert mut_diff > 0, "G7 never differs"
    rep["w2_differs_from_w1"] = mut_diff
    for k in (2, 5, 12, 20):
        p, top = A.ladder(k)
        rc = S.carried_phases(p, 2, keep=True)
        rn = S.carried_phases(p, 2, keep=False)
        assert rc["P"] == 1 and rc["phase"][top] == 1, "G6 keep"
        assert rn["phase"][top] == math.ceil((k + 1) / 2), "G6 spend"
    rep["G6"] = "ladder: one phase with two carried distinctions and keeping"
    # G8: h held; chains h-u1-..-x and h-v1-..-y of links (helper g held)
    atoms, n = [], 0
    hh, g = 0, 1
    n = 2
    def chain(start, L):
        nonlocal n
        prev = start
        for _ in range(L):
            atoms.append((prev, g, n)); prev = n; n += 1
        return prev
    x = chain(hh, 4)
    y = chain(hh, 4)
    c = n; n += 1
    t = n; n += 1
    atoms += [(x, y, c), (c, x, t)]
    p = A.Pattern(n, atoms, [hh, g])
    f, _, _ = A.native_rounds(p)
    assert f[t]
    k2 = S.carried_phases(p, 2, keep=True)
    s2 = S.carried_phases(p, 2, keep=False)
    s3 = S.carried_phases(p, 3, keep=False)
    assert k2["phase"][t] == 1 and s2["phase"][t] == 1 and s3["phase"][t] == 1, "G8"
    rep["G8"] = {"keep_w2": int(k2["phase"][t]), "spend_w2": int(s2["phase"][t]), "spend_w3": int(s3["phase"][t])}
    rep["status"] = "all gates passed"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "gates.json"), "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
