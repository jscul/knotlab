#!/usr/bin/env python3
"""Checks for LEARN-HANDLES-20261109-001A: learning resolves a class-forced pair only by winding.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, a few minutes. Exact on the spaces stated: every least state up to 20 points, 200 sampled by SAT beyond (seeded). Checks 4
to 6 are computations, not theorems; check 6 is the stress test of RESIGN-STEER-20261107-001B's local rule one size past."""
import hashlib
import importlib.util
import json
import math
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import handles_lib as H  # noqa: E402

T0 = time.time()
OUT = {}
DEPS = {
    "proofs/COUNT-SURFACES-20261107-001A/COUNT-SURFACES-20261107-001A-P001_the_count_reads_the_euler_characteristic/surface_lib.py":
        "49cc570c49a8617e5de070be79bae06ba995c7ce25894ad263022522d0ea8943",
    "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py":
        "ce5b9e284489ed3f1c60d5768be985d7966e27ac1ecea3b247fab47c3c439a2b",
    "experiments/RESIGN-STEER-20261107-001B/RESIGN-STEER-20261107-001B-E001_local_rules_and_the_force_between_halves/run.py":
        "c075646983d6710ad642752112e547b894da23364e753bd0091f8a22a5296793",
    "research/LEARN-HANDLES-20261109-001/preregistration.md":
        "17678476e0cd1067ce534cc326e31fd63994f35f178238f8c28a047d393872cb",
}
BRUTE, SAMPLE = 20, 200


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def lower_bound(T, delta):
    """the fewest sides of a cycle of T (an even subgraph) in class delta: one closed walk of that class, or two of the other two"""
    sys_ = {d: T.systole(d) for d in H.LABELS[1:]}
    a, b = [d for d in H.LABELS[1:] if d != delta]
    return min(sys_[delta], sys_[a] + sys_[b])


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        # networkx's matchings in check 6 iterate over hashed string-tuple nodes: fix the hash seed so the run reproduces
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    check("0 dependencies bound by hash", all(sha(p) == h for p, h in DEPS.items()), sorted(DEPS))

    # ------------------------------------------------------------------------------------------------ 1 the spaces
    tori = []
    for t in H.class_forced_tori(40):
        T = H.Torus(*t)
        sat = {lab for lab, s in T.classes.items() if T.K.sat(s)[0]}
        assert sat == T.sat, t
        tori.append(T)
    info = {"tori": len(tori), "Fano": 2, "thin, even index 4 to 40": len(tori) - 2,
            "one class unsatisfiable on each": all(len(T.forced) == 1 for T in tori)}
    check("1 class-forced spaces: the two Fano tori and 57 thin tori of even index up to 40 points, each with exactly one sign class "
          "that no state satisfies (SAT agrees with the criterion of COUNT-SURFACES-20261107-001A theorem 5)", info["one class unsatisfiable on each"], info)

    # ------------------------------------------------------------------------------------------------ 2 least states (E1)
    rng = random.Random(20261109)
    least, rows = {}, []
    for T in tori:
        s = T.classes[T.forced[0]]
        if T.n <= BRUTE:
            m, xs = T.least_states_brute(s)
            how = "all"
        else:
            m, xs = 1, T.least_states_sat(s, rng, SAMPLE)
            how = "SAT sample"
        ok = m == 1 and len(xs) > 0
        for x in xs:
            viol, deg, D, E = T.tally(s, x)
            ok &= len(viol) == 1 and E == 1 and D == [] and sorted(deg) == [1] * (T.V - 1) + [3]
        least[T.name] = xs
        rows.append({"torus": T.name, "points": T.n, "least violated lines": m, "least states": len(xs), "read": how, "ok": bool(ok)})
    thin_sq = all(r["least states"] == r["points"] ** 2 for r in rows[2:] if r["read"] == "all")
    check("2 E1: every class-forced law has states violating exactly one line, and each of them has exactly one face whose three corners all "
          "agree (deg 3), every other face deg 1; up to 20 points every least state is read (70 on each Fano torus, n^2 on each thin torus), "
          "beyond, 200 found by SAT", all(r["ok"] for r in rows) and thin_sq,
          {"rows": rows, "thin tori up to 20 points have n^2 least states": thin_sq})

    # ------------------------------------------------------------------------------------------------ 3 learning resolves, and winds (E2)
    E2, cost_rows = [], []
    tot = Counter()
    for T in tori:
        w = T.forced[0]
        s = T.classes[w]
        lb = {d: lower_bound(T, d) for d in H.LABELS[1:]}
        costs = {c: [] for c in H.LABELS if c != w}
        r = Counter()
        for x in least[T.name]:
            for k in range(3):
                s2, f, deg, l0, w0 = T.split(s, x, k)
                direct = None
                for c in costs:
                    M, cost = T.cheapest_matching(f, c)
                    r["walks"] += 1
                    if M is None:
                        r["class not reached"] += 1
                        continue
                    moves, left = T.realize(f, deg, M)
                    if left:
                        r["alternating cycle left (detour needed)"] += 1
                        continue
                    sf, local = T.replay(s2, x, moves)
                    viol, dg, D, E = T.tally(sf, x)
                    z = [a ^ b for a, b in zip(sf, s)]
                    delta = T.label(z)
                    n_resign = 1 + len(moves)
                    # z is a cycle: re-signing it on the Kasteleyn signing 0 keeps every face odd
                    zero_flip = T.K.even_faces(z) == T.K.even_faces([0] * len(z))
                    ok = (local and not viol and E == 0 and not D and T.label(sf) == c and delta != (0, 0) and zero_flip
                          and tuple(a ^ b for a, b in zip(w, c)) == delta and len(moves) == cost and lb[delta] <= sum(z) <= n_resign)
                    r["resolved and winding" if ok else "FAILED"] += 1
                    costs[c].append(n_resign)
                    direct = n_resign if direct is None else min(direct, n_resign)
                r["cheapest walk over classes found"] += direct is not None
        tot.update(r)
        E2.append({"torus": T.name, **dict(r)})
        cost_rows.append({"torus": T.name, "points": T.n, "by class change": {
            "%d%d" % tuple(a ^ b for a, b in zip(w, c)): {"lower bound (systole)": lb[tuple(a ^ b for a, b in zip(w, c))],
                                                          "cheapest": min(v), "mean": round(float(np.mean(v)), 2), "most": max(v)}
            for c, v in costs.items() if v}})
    ok3 = tot["FAILED"] == 0 and tot["class not reached"] == 0 and tot["resolved and winding"] + tot["alternating cycle left (detour needed)"] == tot["walks"]
    check("3 E2: from every least state read and each of its three splits, learning at the dissonance with the state fixed resolves the pair into "
          "every other class (cheapest perfect matching of that class, holes moved along lines that agree where they go): every step is at a "
          "dissonance, the end has no violated line, no over-agreeing face and no even face, and the sign change is a cycle whose class is the "
          "difference of classes, never zero", ok3, {"totals": dict(tot), "per torus": E2})

    # ------------------------------------------------------------------------------------------------ 4 cost against the systole (E4)
    check("4 E4 (computed): the cheapest walk into each class, against the least number of sides of a cycle in its class change", True,
          {"rows": cost_rows})

    # ------------------------------------------------------------------------------------------------ 5 a local rule (E5)
    rule_rows = []
    rr = random.Random(5)
    for T in tori:
        w = T.forced[0]
        s = T.classes[w]
        xs = least[T.name]
        pick = xs if len(xs) <= SAMPLE else rr.sample(xs, SAMPLE)
        row = Counter()
        rand_steps, nr_steps, nr_cost_excess = [], [], []
        lb = {d: lower_bound(T, d) for d in H.LABELS[1:]}
        for x in pick:
            k = rr.randrange(3)
            s2, f, deg, l0, w0 = T.split(s, x, k)
            for rule, budget in (("no_reversal", 20 * T.V), ("random", 50 * T.V * T.V)):
                if rule == "random" and row["random runs"] >= 50:
                    continue
                okr, steps, moves = T.run_rule(f, deg, w0, rule, rr, budget)
                row[rule + " runs"] += 1
                if okr:
                    sf, local = T.replay(s2, x, moves)
                    viol, dg, D, E = T.tally(sf, x)
                    z = [a ^ b for a, b in zip(sf, s)]
                    good = local and not viol and E == 0 and not D and T.label(z) != (0, 0)
                    row[rule + " resolved" if good else rule + " REPLAY FAILED"] += 1
                    if rule == "random":
                        rand_steps.append(steps)
                    else:
                        nr_steps.append(steps + 1)
                        nr_cost_excess.append(steps + 1 - lb[T.label(z)])
                        row["no_reversal class change %d%d" % T.label(z)] += 1
                elif rule == "no_reversal":
                    ok10, st10, _ = T.run_rule(f, deg, w0, rule, rr, 10 * budget)
                    row["no_reversal failed; resolved with 10x budget" if ok10 else "no_reversal failed; not with 10x budget"] += 1
                else:
                    row["random not resolved within budget"] += 1
        rule_rows.append({"torus": T.name, "points": T.n, **dict(row),
                          "no_reversal mean re-signings": round(float(np.mean(nr_steps)), 2) if nr_steps else None,
                          "no_reversal mean excess over lower bound": round(float(np.mean(nr_cost_excess)), 2) if nr_cost_excess else None,
                          "random mean re-signings": round(float(np.mean(rand_steps)), 1) if rand_steps else None})
    bad = sum(r.get("no_reversal REPLAY FAILED", 0) + r.get("random REPLAY FAILED", 0) for r in rule_rows)
    nr_tot = sum(r["no_reversal runs"] for r in rule_rows)
    nr_ok = sum(r.get("no_reversal resolved", 0) for r in rule_rows)
    check("5 E5 (computed, exploratory): a rule seeing only the lines at a hole and the outside distance to the over-agreeing face, never stepping "
          "straight back, and unbiased random moves; every resolved run replays as sign changes at the dissonance and winds", bad == 0,
          {"no_reversal resolved": nr_ok, "of": nr_tot, "rows": rule_rows})

    # ------------------------------------------------------------------------------------------------ 6 the sphere's rule one size past (S)
    spec = importlib.util.spec_from_file_location("steer_run", ROOT / list(DEPS)[2])
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    L = R.L
    srng = random.Random(1107)
    spheres = [(L.octahedral(m), 40 * m) for m in (14, 16)]
    spheres += [(K, 20 * math.ceil(math.sqrt(K.V))) for K in L.test_spheres(srng)]
    srows = []
    for K, budget in spheres:
        ok, fails, ratio = 0, [], []
        trials = []
        while len(trials) < 300:
            l, match, holes = R.start(K, srng)
            t = srng.randrange(K.V)
            if t not in holes:
                trials.append((l, match, holes, t))
        for (l, match, holes, t) in trials:
            r, st, path = R.run_rule(K, match, holes, t, "no_reversal", srng, budget)
            d0 = min(K.dist(t)[holes[0]], K.dist(t)[holes[1]])
            if r:
                ok += 1
                ratio.append(st / max(d0, 1))
            else:
                r10, st10, _ = R.run_rule(K, match, holes, t, "no_reversal", srng, 10 * budget)
                fails.append({"start distance": d0, "reached with 10x budget": r10})
        rep = []
        for (l, match, holes, t) in trials[:5]:
            r, st, path = R.run_rule(K, match, holes, t, "no_reversal", random.Random(1), budget)
            dt = K.dist(t)
            j = 0 if dt[holes[0]] <= dt[holes[1]] else 1
            rep.append(R.replay_ok(K, l, match, holes, path, holes[1 - j]))
        srows.append({"sphere": K.name, "faces": K.V, "budget": budget, "reached": ok, "of": 300,
                      "mean steps / start distance": round(float(np.mean(ratio)), 2) if ratio else None, "failures": fails,
                      "replayed as sign changes": all(rep)})
        print("  sphere", K.name, ok, "/ 300", flush=True)
    s_ok = all(r["replayed as sign changes"] for r in srows)
    check("6 S (stress test, computed): RESIGN-STEER-20261107-001B's no-reversal rule on K_14 and K_16 and on the non-octahedral test spheres, "
          "300 random targets each; pass when every sphere reaches at least 95%", s_ok,
          {"rows": srows, "at least 95% on every sphere": all(r["reached"] >= 285 for r in srows)})

    OUT["seconds"] = round(time.time() - T0, 1)
    res = HERE / "result.json"
    if write:
        res.write_text(json.dumps({"status": "passed", "checks": OUT}, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())["checks"]
        fresh = json.loads(json.dumps(OUT, default=str))
        diff = [k for k in OUT if k != "seconds" and json.dumps(old.get(k, {}).get("info"), sort_keys=True)
                != json.dumps(fresh[k]["info"], sort_keys=True)]
        same = not diff
        print("result.json reproduced" if same else "result.json differs: %s" % diff)
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
