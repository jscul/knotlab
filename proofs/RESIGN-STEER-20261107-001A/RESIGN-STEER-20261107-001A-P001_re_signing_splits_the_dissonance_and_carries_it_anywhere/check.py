#!/usr/bin/env python3
"""Checks for RESIGN-STEER-20261107-001A: re-signing splits the forced dissonance and carries it anywhere.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (pysat, numpy, networkx). Single process; about ten minutes."""
import hashlib
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import steer_lib as L  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sat(K, s):
    from pysat.solvers import Solver
    with Solver(name="cadical153", bootstrap_with=K.K.clauses(s)) as so:
        r = so.solve()
        return bool(r), (so.get_model() if r else None)


def brute_flat_counts(K):
    """every assignment of K_2 under the Kasteleyn signing: the number with exactly one violated line and no over-agreement, by line"""
    n = K.n
    X = np.arange(1 << n, dtype=np.int64)
    lit = [[((X >> K.pt[i][k]) & 1) ^ K.s0[3 * i + k] for k in range(3)] for i in range(n)]
    agree = [[(lit[i][(c + 1) % 3] == lit[i][(c + 2) % 3]).astype(np.int64) for c in range(3)] for i in range(n)]
    viol = [(agree[i][0] + agree[i][1] + agree[i][2]) == 3 for i in range(n)]
    nviol = sum(v.astype(np.int64) for v in viol)
    face = [np.zeros(1 << n, dtype=np.int64) for _ in range(K.V)]
    for i in range(n):
        for c in range(3):
            face[K.fv[i][c]] += agree[i][c]
    E = sum(f // 2 for f in face)
    flat = (nviol == 1) & (E == 0)
    return [int((flat & viol[i]).sum()) for i in range(n)]


def brute_sat_count(K, s):
    n = K.n
    X = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    for i in range(n):
        ys = [((X >> K.pt[i][k]) & 1) ^ s[3 * i + k] for k in range(3)]
        ok &= ~((ys[0] == ys[1]) & (ys[1] == ys[2]))
    return int(ok.sum())


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    rng = random.Random(20261107)
    spheres = L.test_spheres(rng)
    octa = {m: (L.octahedral(m) if m > 4 else next(S for S in spheres if S.name == f"K_{m}")) for m in (2, 3, 4, 5, 6)}

    # 1 bookkeeping: viol - E + |D|/2 = 1 in every state and law; one re-signing moves at most one unit between state and law
    rows, ok = [], True
    for K in spheres:
        bad1 = moves = 0
        for _ in range(20):
            s = [rng.randrange(2) for _ in range(3 * K.n)]
            x = [rng.randrange(2) for _ in range(K.n)]
            v, _, D, E = K.tally(s, x)
            bad1 += (len(v) - E + len(D) / 2) != 1
            e = rng.randrange(3 * K.n)
            s2 = list(s)
            s2[e] ^= 1
            v2, _, D2, E2 = K.tally(s2, x)
            dD = (len(D2) - len(D)) // 2
            bad1 += (len(v2) - E2) - (len(v) - E) != -dD or abs(dD) > 1
            moves += dD != 0
        rows.append([K.name, bad1, moves])
        ok &= bad1 == 0
    # over-rationalization: with four even faces every satisfying state over-agrees somewhere
    K = octa[3]
    over = []
    for _ in range(10):
        D = rng.sample(range(K.V), 4)
        s = K.K.signing(D)
        r, model = sat(K, s)
        if r:
            x = [int(model[p] > 0) for p in range(K.n)]
            over.append(K.tally(s, x)[3])
    ok &= len(over) > 0 and min(over) >= 1
    check("1 bookkeeping: violated lines - E + |D|/2 = 1 for random laws and states; one re-signing moves at most one unit; with four "
          "even faces satisfying states over-agree", ok, {"[sphere, failures, re-signings that moved a unit]": rows,
                                                         "E of satisfying states with |D| = 4 on K_3": over})

    # 2 every law with exactly two even faces is satisfiable, wherever they sit (theorem 2)
    rows, ok = [], True
    for K in [octa[m] for m in (2, 3, 4, 5, 6)] + [S for S in spheres if not S.name.startswith("K_")]:
        unsat = sum(1 for u, v in itertools.combinations(range(K.V), 2) if K.pm({u, v}) is None)
        rows.append([K.name, K.n, K.girth_ok(), K.V * (K.V - 1) // 2, unsat])
        ok &= unsat == 0 or not K.girth_ok()
    K = octa[2]
    sat_all = all(sat(K, K.K.signing((u, v)))[0] for u, v in itertools.combinations(range(K.V), 2))
    K3 = octa[3]
    sample = rng.sample(list(itertools.combinations(range(K3.V), 2)), 40)
    sat_some = all(sat(K3, K3.K.signing(p))[0] for p in sample)
    counts = []
    for u, v in rng.sample(list(itertools.combinations(range(K.V), 2)), 20):
        s = K.K.signing((u, v))
        counts.append([u, v, brute_sat_count(K, s), 2 * round(math.exp(K.count_pm({u, v})))])
    ok &= sat_all and sat_some and all(c[2] == c[3] for c in counts)
    check("2 every law with exactly two even faces is satisfiable, wherever they sit (all pairs; SAT agrees; satisfying assignments = "
          "2 x matchings)", ok, {"[sphere, points, girth >= 6, pairs, unsatisfiable pairs]": rows, "K_2 all pairs SAT": sat_all,
                                 "K_3 40 pairs SAT": sat_some, "[u, v, brute count, 2 #PM] on K_2": counts})

    # 3 every line is the only violated line of a flat state of the Kasteleyn law (corollary 2b)
    rows = []
    for m in (2, 3, 4, 5, 6):
        K = octa[m]
        for l in range(K.n):
            K.flat_state(l)       # asserts one violated line, l, and E = 0
        rows.append([K.name, K.n])
    check("3 on K_2..K_6 every line is the only violated line of some flat state (one violated line, no over-agreement)", True,
          {"[sphere, lines, all built]": rows})

    # 4 uniformity (theorem 3)
    rows, ok = [], True
    for K in [octa[m] for m in (2, 3, 4, 5, 6)] + [S for S in spheres if not S.name.startswith("K_")]:
        if not K.girth_ok():
            continue
        B = K.incidence()
        col = K.three_colouring()
        f1 = np.array([(c == 0) - (c == 1) for c in col], float)
        f2 = np.array([(c == 0) - (c == 2) for c in col], float)
        kern = bool(np.linalg.matrix_rank(B) == K.n and np.allclose(B @ f1, 0) and np.allclose(B @ f2, 0))
        vals = [K.count_pm(set(K.fv[l][:2])) for l in range(K.n)]
        logN, ns = K.closed_form_logN()
        N = math.exp(vals[0])
        pairs = list(itertools.combinations(range(K.V), 2))
        bic = [p for p in pairs if col[p[0]] != col[p[1]]]
        same = [p for p in pairs if col[p[0]] == col[p[1]]]
        bic_s, same_s = rng.sample(bic, min(15, len(bic))), rng.sample(same, min(15, len(same)))
        minors_ok = all(abs(K.allplus_minor(u, v, B) - N) < 1e-6 * N for u, v in bic_s) and \
            all(K.allplus_minor(u, v, B) < 1e-6 * N for u, v in same_s)
        lower_ok = all(K.count_pm({u, v}) >= vals[0] - 1e-9 for u, v in bic_s)
        spread = max(vals) - min(vals)
        rows.append([K.name, K.n, ns, round(N) if N < 1e15 else "%.6e" % N, spread, abs(logN - vals[0]), kern, minors_ok, lower_ok])
        ok &= kern and spread < 1e-9 and abs(logN - vals[0]) < 1e-9 and minors_ok and lower_ok
    K = octa[2]
    brute = brute_flat_counts(K)
    ok &= set(brute) == {108}
    check("4 every line is the violated line of equally many flat states, 2 N(T) with N(T)^2 = det(B B^T)/e2(colour classes); the kernel "
          "is the 3-colourings; all-plus minors are N on differently coloured pairs and 0 on equal colours; #PM >= N on differently "
          "coloured pairs", ok, {"[sphere, n, colour classes, N(T), spread of log counts over lines, |closed form - count|, kernel = "
                                 "3-colourings, minors, lower bound]": rows, "K_2 flat states per line by brute force": sorted(set(brute))})

    # 5 steering with the state fixed (theorem 4)
    rows, ok = [], True
    for m in (2, 3, 4, 5, 6):
        K = octa[m]
        pairs = [(a, b) for a in range(K.n) for b in range(K.n)] if m <= 3 else \
            [(rng.randrange(K.n), rng.randrange(K.n)) for _ in range(150)]
        kinds, steps, gauge_ok, x_fixed = set(), [], True, True
        for j, (l0, t) in enumerate(pairs):
            x0 = K.flat_state(l0)
            s, x, tallies, nst, local = K.steer(l0, t, list(x0))
            x_fixed &= x == x0
            kinds |= {(len(v), E, len(D)) for v, _, D, E in tallies}
            v, _, D, E = tallies[-1]
            ok &= v == [t] and D == [] and E == 0 and local
            steps.append(nst)
            if j % 7 == 0:
                pts, _ = K.gauge_region(s)
                y = list(x)
                for p in pts:
                    y[p] ^= 1
                v2, _, D2, E2 = K.tally(K.s0, y)
                gauge_ok &= v2 == [t] and D2 == [] and E2 == 0
        rows.append([K.name, len(pairs), sorted(kinds), max(steps), round(sum(steps) / len(steps), 1), gauge_ok])
        ok &= kinds <= {(1, 0, 0), (0, 0, 2)} and gauge_ok and x_fixed
    check("5 re-signings at the dissonance carry it from any line to any line with the state fixed; every intermediate configuration "
          "is (1 violated line, E 0, no even face) or (none, E 0, two even faces); the closed walk is a block change of state", ok,
          {"[sphere, start/target pairs, (viol, E, |D|) seen, max re-signings, mean, block-change check]": rows})

    # 6 controls
    ctl = {}
    K = octa[3]
    ctl["Kasteleyn law unsatisfiable (K_2..K_4)"] = all(not sat(octa[m], octa[m].s0)[0] for m in (2, 3, 4))
    K4 = octa[4]
    far = [K4.count_pm({0, v}) for v in range(1, K4.V)]
    ctl["counts over all pairs from one face are not uniform on K_4 (log spread)"] = max(far) - min(far)
    x0 = K.flat_state(0)
    s = list(K.s0)
    a, b, _ = K.fv[0]
    s[3 * 0 + K.side_between(0, a, b)] ^= 1
    # re-sign a side of a satisfied line far from both even faces: not local, and it leaves the two allowed kinds
    v, _, D, _ = K.tally(s, x0)
    far_line = next(i for i in range(K.n) if i not in v and not set(K.fv[i]) & set(D))
    s[3 * far_line] ^= 1
    v2, _, D2, E2 = K.tally(s, x0)
    ctl["a re-signing away from the dissonance leaves the allowed configurations"] = (len(v2), E2, len(D2)) not in {(1, 0, 0), (0, 0, 2)}
    B = K4.incidence()
    col = K4.three_colouring()
    u, w = max(((u, w) for u, w in itertools.combinations(range(K4.V), 2) if col[u] != col[w]), key=lambda p: K4.dist(p[0])[p[1]])
    ctl["far differently coloured pair: all-plus minor below the count (log gap)"] = K4.count_pm({u, w}) - math.log(K4.allplus_minor(u, w, B))
    okc = ctl["Kasteleyn law unsatisfiable (K_2..K_4)"] and \
        ctl["counts over all pairs from one face are not uniform on K_4 (log spread)"] > 0.5 and \
        ctl["a re-signing away from the dissonance leaves the allowed configurations"] and \
        ctl["far differently coloured pair: all-plus minor below the count (log gap)"] > 0.5
    check("6 controls: each check can fail", okc, ctl)

    # 7 one size past: K_7 and K_8
    rows, ok = [], True
    for m in (7, 8):
        K = L.octahedral(m)
        single = sum(1 for e in range(3 * K.n) if K.pm({K.fv[e // 3][(e % 3 + 1) % 3], K.fv[e // 3][(e % 3 + 2) % 3]}) is None)
        pairs = rng.sample(list(itertools.combinations(range(K.V), 2)), 300)
        unsat = sum(1 for p in pairs if K.pm(set(p)) is None)
        vals = [K.count_pm(set(K.fv[l][:2])) for l in range(K.n)]
        logN, ns = K.closed_form_logN()
        good = 0
        for _ in range(30):
            l0, t = rng.randrange(K.n), rng.randrange(K.n)
            s, x, tallies, nst, local = K.steer(l0, t)
            good += tallies[-1][0] == [t] and all((len(v), E, len(D)) in {(1, 0, 0), (0, 0, 2)} for v, _, D, E in tallies) and local
        rows.append([K.name, K.n, single, unsat, max(vals) - min(vals), abs(logN - vals[0]), "%.6e" % math.exp(vals[0]), good])
        ok &= single == 0 and unsat == 0 and max(vals) - min(vals) < 1e-8 and abs(logN - vals[0]) < 1e-8 and good == 30
    check("7 one size past (K_7, K_8): every single re-signing and 300 random pairs satisfiable; uniformity over all lines and the closed "
          "form; 30 steering runs each", ok, {"[sphere, n, unsatisfiable single re-signings, unsatisfiable random pairs, spread, |closed "
                                              "form - count|, N, steering runs reached]": rows})

    result = {"status": "passed", "checks": OUT}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: old["checks"].get(k, {}).get("pass") == v["pass"] for k, v in OUT.items()}
        print("matches result.json" if all(same.values()) and old["status"] == "passed" else "DIFFERS from result.json", same)
