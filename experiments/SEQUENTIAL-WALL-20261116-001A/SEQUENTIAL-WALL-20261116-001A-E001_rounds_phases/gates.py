"""Gate checks for SEQUENTIAL-WALL-20261116-001A (run before any read-out).

G1  closure = forced set by exhaustive states (tiny random patterns).
G2  untangling phases end in the same forced set as native rounds, and each
    distinction's phase equals its rank computed by relaxation.
G3  rank <= log2 fringe; mutants (rank with combine = max; phases that also
    read atoms with no forced demander) must disagree somewhere.
G4  monotone circuits: atom-pattern closure and NAE propagation both equal
    circuit evaluation on every gate, all inputs, for small random circuits.
G5  knotlab: the atom and not-all-equal pass K1-K3.
G6  structured families: chain, ladder, pyramid, balanced tree give their
    ranks by construction.
G7  dual law on acyclic patterns: the unforced set is the complement of the
    forced set (by states), each dual phase equals the dual rank by
    relaxation, and a mutant dual rank (plain max) disagrees somewhere;
    unlayered circuits' atom patterns equal their evaluation.
"""

import itertools
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import atoms as A  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "artifacts", "SEQUENTIAL-WALL-20261116-001A",
                   "SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases")


def brute_forced(p):
    """Distinctions equal to 1 in every allowed state with held = 1."""
    n = p.n
    free = [v for v in range(n) if not p.held[v]]
    always = np.ones(n, dtype=bool)
    any_state = False
    for bits in itertools.product((0, 1), repeat=len(free)):
        x = p.held.astype(np.int8).copy()
        x[free] = bits
        if np.all(~(x[p.a].astype(bool) & x[p.b].astype(bool)) | x[p.c].astype(bool)):
            any_state = True
            always &= x.astype(bool)
    assert any_state  # all-ones is always allowed
    return always


def mutant_rank(p):
    r = np.where(p.held, 0, A.INF).astype(np.int64)
    while True:
        cand = np.maximum(r[p.a], r[p.b])
        cand = np.where(cand >= A.INF, A.INF, cand)
        best = np.full(p.n, A.INF, dtype=np.int64)
        np.minimum.at(best, p.c, cand)
        upd = best < r
        if not upd.any():
            return r
        r = np.where(upd, best, r)


def mutant_phases(p):
    """Wrong law: every atom also reads as both rules a -> c and b -> c."""
    forced = p.held.copy()
    phase = np.where(forced, 0, -1)
    t = 0
    while True:
        tails = np.concatenate([p.a, p.b])
        heads = np.concatenate([p.c, p.c])
        new = A._reach(p.n, forced, tails, heads) & ~forced
        if not new.any():
            return forced, phase, t
        t += 1
        forced |= new
        phase[new] = t


def g1_g2_g3(rng, report):
    n_cases = 0
    rank_mut_diff = phase_mut_diff = 0
    for n in range(4, 13):
        for _ in range(60):
            c = rng.choice([0.5, 1.0, 1.5, 2.5, 4.0])
            trip = A.random_pattern(n, c, rng)
            k = int(rng.integers(1, max(2, n // 2)))
            held = rng.choice(n, k, replace=False)
            p = A.Pattern(n, trip, held)
            f_native, when, R = A.native_rounds(p)
            f_phase, phase, P = A.untangling_phases(p)
            r = A.rank(p)
            if n <= 12:
                bf = brute_forced(p)
                assert np.array_equal(bf, f_native), "G1 closure != forced"
            assert np.array_equal(f_native, f_phase), "G2 forced sets differ"
            fin = r < A.INF
            assert np.array_equal(fin, f_native), "G2 rank finite != forced"
            assert np.array_equal(phase[fin], r[fin]), "G2 phase != rank"
            assert P == (r[fin].max() if fin.any() else 0), "G2 P != max rank"
            assert P <= R, "G2 phases exceed rounds"
            lf = A.log2_fringe(p)
            assert np.all(r[fin] <= lf[fin] + 1e-9), "G3 rank > log2 fringe"
            mr = mutant_rank(p)
            rank_mut_diff += int(np.any(mr[fin] != r[fin]))
            fm, _, _ = mutant_phases(p)
            phase_mut_diff += int(np.any(fm != f_native))
            n_cases += 1
    assert rank_mut_diff > 0 and phase_mut_diff > 0, "G3 mutants never disagree"
    report["G1_G2_G3"] = {"cases": n_cases, "rank_mutant_disagrees": rank_mut_diff,
                          "phase_mutant_disagrees": phase_mut_diff}


def g4(rng, report):
    n_circ = n_inputs = 0
    for depth in range(1, 7):
        for width in range(2, 6):
            for _ in range(8):
                first = rng.choice(["AND", "OR"])
                mixed = bool(rng.random() < 0.5)
                _, layers = A.alternating_circuit(depth, width, rng, first=first, mixed=mixed)
                for bits in itertools.product((False, True), repeat=width):
                    inputs = np.array(bits, dtype=bool)
                    vals = A.evaluate_circuit(inputs, layers)
                    p, ids = A.circuit_to_atoms(inputs, layers)
                    forced, _, _ = A.native_rounds(p)
                    for lay, gid in zip(vals, ids):
                        assert np.array_equal(forced[gid], lay), "G4 atoms != circuit"
                    n, triples, assigned, nids = A.circuit_to_nae(inputs, layers)
                    val, _ = A.nae_propagate(n, triples, assigned)
                    assert val is not None, "G4 NAE conflict"
                    for lay, gid in zip(vals, nids):
                        got = np.array([val.get(int(v)) == 1 for v in gid])
                        unset_or_one = all(val.get(int(v)) in (None, 1) for v in gid)
                        assert unset_or_one and np.array_equal(got, lay), "G4 NAE != circuit"
                    n_inputs += 1
                n_circ += 1
    report["G4"] = {"circuits": n_circ, "circuit_inputs": n_inputs}


def g5(report):
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "tools"))
    out = {}
    for name, cnf in [("atom", "~A ~B c"), ("not-all-equal", "A B c; ~A ~B ~c")]:
        res = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
                              "--loops", "A", "B", "--contact", "c", "--json"],
                             capture_output=True, text=True, env=env, cwd=ROOT, check=True)
        d = json.loads(res.stdout)
        assert d.get("is_knot") is True, f"G5 {name} is not a knot"
        out[name] = {k: d[k] for k in ("is_knot", "allowed", "pairwise_definable")}
    report["G5"] = out


def g6(report):
    out = {}
    for L in (1, 5, 40):
        p, top = A.chain(L)
        _, _, R = A.native_rounds(p)
        r = A.rank(p)
        assert R == L and r[top] == 1, "G6 chain"
    for k in (1, 4, 12):
        p, top = A.ladder(k)
        r = A.rank(p)
        assert r[top] == k + 1, "G6 ladder"
    for h in (1, 3, 9):
        p, top = A.pyramid(h)
        r = A.rank(p)
        _, _, R = A.native_rounds(p)
        assert r[top] == h and R == h, "G6 pyramid"
    for d in (1, 3, 8):
        p, top = A.balanced_and_tree(d)
        r = A.rank(p)
        assert r[top] == d, "G6 tree"
    out["chain"] = "R = L, rank 1"
    out["ladder"] = "rank k + 1 at x_k"
    out["pyramid"] = "R = rank = h"
    out["balanced tree"] = "rank = height"
    report["G6"] = out


def acyclic_pattern(n, m, rng):
    trip = []
    for _ in range(m):
        a, b, c = sorted(rng.choice(n, 3, replace=False))
        if rng.random() < 0.5:
            a, b = b, a
        trip.append((a, b, c))
    perm = rng.permutation(n)
    return [(int(perm[a]), int(perm[b]), int(perm[c])) for a, b, c in trip]


def mutant_dual_rank(p):
    order = np.argsort(p.c, kind="stable")
    cs = p.c[order]
    starts = np.searchsorted(cs, np.arange(p.n + 1))
    demanded = starts[1:] > starts[:-1]
    d = np.where(~p.held & ~demanded, 0, A.INF).astype(np.int64)
    while True:
        death = np.minimum(d[p.a], d[p.b])[order]
        mx = np.full(p.n, -1, dtype=np.int64)
        np.maximum.at(mx, cs, death)
        cand = np.where(p.held | ~demanded, d, mx)
        upd = cand < d
        if not upd.any():
            return d
        d = np.where(upd, cand, d)


def g7(rng, report):
    cases = mut = 0
    for n in range(4, 13):
        for _ in range(80):
            m = int(rng.integers(1, 3 * n))
            trip = acyclic_pattern(n, m, rng)
            k = int(rng.integers(0, n))
            held = rng.choice(n, k, replace=False) if k else []
            p = A.Pattern(n, trip, held)
            bf = brute_forced(p)
            unf, dph, Pd = A.dual_phases(p)
            dr = A.dual_rank(p)
            assert np.array_equal(unf, ~bf), "G7 unforced != complement"
            fin = dr < A.INF
            assert np.array_equal(fin, unf), "G7 dual rank finite != unforced"
            assert np.array_equal(dph[fin], dr[fin]), "G7 dual phase != dual rank"
            assert Pd == (int(dr[fin].max()) + 1 if fin.any() else 0), "G7 P_dual"
            mut += int(np.any(mutant_dual_rank(p)[fin] != dr[fin]))
            cases += 1
    assert mut > 0, "G7 mutant never disagrees"
    circ = 0
    for _ in range(200):
        n_in = int(rng.integers(2, 6))
        inputs, gates_ = A.unlayered_circuit(n_in, int(rng.integers(1, 30)), rng)
        p, node, vals = A.unlayered_to_atoms(inputs, gates_)
        f, _, _ = A.native_rounds(p)
        assert np.array_equal(f[node], vals), "G7 unlayered != evaluation"
        unf, _, _ = A.dual_phases(p)
        assert np.array_equal(unf[node], ~vals), "G7 unlayered dual"
        circ += 1
    report["G7"] = {"acyclic_cases": cases, "dual_mutant_disagrees": mut, "unlayered_circuits": circ}


def main():
    rng = np.random.default_rng(20261116)
    report = {}
    g1_g2_g3(rng, report)
    g4(rng, report)
    g5(report)
    g6(report)
    g7(rng, report)
    report["status"] = "all gates passed"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "gates.json"), "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    print(json.dumps(report, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
