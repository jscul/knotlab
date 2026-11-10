#!/usr/bin/env python3
"""Checks for GROW-HANDLE-20261110-001A: a Fano atom grown at a knot sphere's dissonance.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, a few minutes, PYTHONHASHSEED=0. Check 1 tests the builder on its own. Checks 2-4 are exact on the spaces stated; checks 5 and
6 are computations."""
import hashlib
import importlib.util
import json
import os
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import grow_lib as G  # noqa: E402

SL, H = G.SL, G.H
T0 = time.time()
OUT = {}
DEPS = {
    "proofs/COUNT-SURFACES-20261107-001A/COUNT-SURFACES-20261107-001A-P001_the_count_reads_the_euler_characteristic/surface_lib.py":
        "49cc570c49a8617e5de070be79bae06ba995c7ce25894ad263022522d0ea8943",
    "proofs/RESIGN-STEER-20261107-001A/RESIGN-STEER-20261107-001A-P001_re_signing_splits_the_dissonance_and_carries_it_anywhere/steer_lib.py":
        "ce5b9e284489ed3f1c60d5768be985d7966e27ac1ecea3b247fab47c3c439a2b",
    "research/GROW-HANDLE-20261110-001/preregistration.md": None,
}
NATIVE = "experiments/NATIVE-TARGET-20261110-001A/NATIVE-TARGET-20261110-001A-E001_native_signals_that_steer_learning/run.py"
HANDLES = "proofs/LEARN-HANDLES-20261109-001A/LEARN-HANDLES-20261109-001A-P001_learning_resolves_a_class_forced_pair_only_by_winding/handles_lib.py"


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:700], round(time.time() - T0, 1), "s", flush=True)
    if not ok and not os.environ.get("NOEXIT"):
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def least_one(K, s):
    """states violating exactly one line (enumeration)"""
    import numpy as np
    n = K.n
    X = np.arange(1 << n, dtype=np.int64)
    viol = np.zeros(1 << n, dtype=np.int8)
    for i in range(n):
        ys = [((X >> K.pt[i][k]) & 1) ^ s[3 * i + k] for k in range(3)]
        viol += ((ys[0] == ys[1]) & (ys[1] == ys[2])).astype(np.int8)
    return int((viol == 1).sum()), int(viol.min())


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    write = "--write" in sys.argv
    DEPS["research/GROW-HANDLE-20261110-001/preregistration.md"] = sha("research/GROW-HANDLE-20261110-001/preregistration.md")
    check("0 dependencies bound by hash", all(sha(p) == h for p, h in DEPS.items()), {p: h for p, h in DEPS.items()})

    # ------------------------------------------------------------------------------------------------ 1 the builder
    rows, ok1 = [], True
    for name, S in [("K_2", SL.octahedral_sphere(2)), ("K_3", SL.octahedral_sphere(3)), ("K_4", SL.octahedral_sphere(4)),
                    ("Fano torus(7,2,1)", SL.torus(7, 2, 1)), ("thin torus(6,1,1)", SL.torus(6, 1, 1)), ("torus(4,2,3)", SL.torus(4, 2, 3))]:
        m = G.rotation_of(S, "A")
        S2 = G.build("rebuilt", *m)
        K, K2 = SL.KnotSpace(S), SL.KnotSpace(S2)
        row = {"space": name, "triangles": (S.nt, S2.nt), "faces": (S.nv, S2.nv), "chi": (S.euler(), S2.euler(), G.euler_of(m)),
               "valid and orientable": S2.validate() and S2.orientable(), "line corners per face": sorted(K.d) == sorted(K2.d)}
        good = S.nt == S2.nt and S.nv == S2.nv and S.euler() == S2.euler() == G.euler_of(m) and row["valid and orientable"] \
            and row["line corners per face"]
        if K.n <= 16:
            a, b = least_one(K, K.signing(())), least_one(K2, K2.signing(()))
            row["states violating one line, least violation"] = (a, b)
            good &= a == b
        if K.chi == 0:
            T1, T2 = G.GrownTorus(S, name, K.signing(())), G.GrownTorus(S2, name, K2.signing(()))
            row["unsatisfiable classes"] = (len(T1.forced), len(T2.forced))
            good &= len(T1.forced) == len(T2.forced)
        row["agree"] = bool(good)
        ok1 &= good
        rows.append(row)
    check("1 the builder: rebuilt from their own rotation systems, K_2-K_4 and three tori (the Fano torus, a thin torus, a torus with every "
          "class satisfiable) keep their triangles, faces, line corners per face, Euler characteristic and orientability; K_2 and the Fano torus "
          "keep their numbers of states violating one line, and the tori their numbers of unsatisfiable classes", ok1, {"rows": rows})

    # ------------------------------------------------------------------------------------------------ the growths
    spec = importlib.util.spec_from_file_location("steer_lib", ROOT / list(DEPS)[1])
    L = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(L)
    spec = importlib.util.spec_from_file_location("native_run", ROOT / NATIVE)
    R = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(R)
    fano = SL.torus(7, 2, 1)
    P = next(t for t in range(fano.nt) if fano.colour[t] == 0)
    sigmas = [tuple(p) for p in __import__("itertools").permutations(range(3))]
    rng = random.Random(1110)
    H1, H2, H34, H5 = [], [], [], []
    tot = Counter()
    for k in (2, 3, 4):
        S = SL.octahedral_sphere(k)
        sph = L.Sphere(S, f"K_{k}")
        KA, s0 = sph.K, sph.s0
        reps, orbit = G.line_orbits(S)
        for l0 in reps:
            x = sph.flat_state(KA.lines.index(l0))
            dist = G.line_distance(S, l0)
            places = [(0, l0)] + [(d, min(t for t, dd in dist.items() if dd == d)) for d in range(1, 5) if d in dist.values()]
            for d, l in places:
                for chir in (0, 1):
                    for sg in sigmas:
                        g = G.Growth(S, s0, l, fano, P, sg, chir)
                        tot["splices"] += 1
                        if g.chi != 0:
                            tot["splices not on a torus (chi %d)" % g.chi] += 1
                            continue
                        tot["splices on a torus"] += 1
                        labs = set()
                        T = None
                        for c in g.completions:
                            T = T or G.GrownTorus(g.G, f"K_{k}+atom", c)
                            labs.add(T.label(c))
                        h1 = len(g.completions) == 2 and len(labs) == 1 and T.simple
                        H1.append(h1)
                        s_nat = T.classes[T.natural]
                        rel = {lab: g.atom_relation(s) for lab, s in T.classes.items()}
                        li = KA.lines.index(l)
                        own = [p for p in __import__("itertools").product((0, 1), repeat=3)
                               if not (p[0] ^ s0[3 * li] == p[1] ^ s0[3 * li + 1] == p[2] ^ s0[3 * li + 2])]
                        acts_as_line = sorted(map(tuple, rel[T.natural])) == own
                        transparent = all(len(r) == 8 for lab, r in rel.items() if lab != T.natural)
                        h2 = T.natural in T.forced and len(T.forced) == 1 and acts_as_line and transparent
                        H2.append(h2)
                        tot["atom acts as the replaced line in the grown class"] += acts_as_line
                        tot["atom transparent in the other three classes"] += transparent
                        tot["grown law unsatisfiable"] += T.natural in T.forced
                        tot["exactly one class unsatisfiable"] += len(T.forced) == 1
                        if not (h1 and h2):
                            continue
                        # the extended state and learning
                        xg, vmin, ties = g.extend(s_nat, x, KA)
                        viol, deg, D, E = T.tally(s_nat, xg)
                        where = "atom" if viol and viol[0] in g.atom_lines else "old"
                        row = {"sphere": f"K_{k}", "l0": l0, "orbit size": sum(1 for t in orbit if orbit[t] == l0), "distance": d,
                               "chirality": chir, "sigma": sg, "extension violates": vmin, "violated line in": where}
                        if vmin != 1:
                            row["walks"] = "skipped: the extension is not a least state"
                            H34.append(row)
                            continue
                        costs, winds, good = {}, True, True
                        for kk in range(3):
                            s2, f, dg, ll, w0 = T.split(s_nat, xg, kk)
                            for c in T.classes:
                                if c == T.natural:
                                    continue
                                M, cost = T.cheapest_matching(f, c)
                                moves, left = T.realize(f, dg, M)
                                if left:
                                    good = False
                                    continue
                                sf, local = T.replay(s2, xg, moves)
                                v2, _, D2, E2 = T.tally(sf, xg)
                                z = [a ^ b for a, b in zip(sf, s_nat)]
                                lab = T.label(z)
                                good &= local and not v2 and E2 == 0 and not D2 and lab != (0, 0) and T.label(sf) == c
                                winds &= any(z[e] for e in g.atom_sides | set(g.new_sides))
                                costs.setdefault("%d%d" % tuple(a ^ b for a, b in zip(T.natural, c)), []).append(1 + len(moves))
                                tot["walks"] += 1
                        row["cheapest walk by class change"] = {cc: min(v) for cc, v in sorted(costs.items())}
                        row["cheapest walk"] = min(min(v) for v in costs.values())
                        row["every walk resolves, winds and touches the atom"] = bool(good and winds)
                        H34.append(row)
                        # rules (one seeded split)
                        s2, f, dg, ll, w0 = T.split(s_nat, xg, rng.randrange(3))
                        r5 = {}
                        for rule in ("R0", "R3"):
                            okr, steps, moves = R.run(T, None, R.Conf(f, dg, s2), rule, rng, 50 * T.V * T.V)
                            r5[rule] = (okr, steps, okr and R.replay_ok(T, s2, xg, moves, s_nat))
                        okr, steps, moves = T.run_rule(f, dg, w0, "no_reversal", rng, 50 * T.V * T.V)
                        r5["R7"] = (okr, steps, okr and R.replay_ok(T, s2, xg, moves, s_nat))
                        H5.append({"sphere": f"K_{k}", "l0": l0, "distance": d, "chirality": chir, "sigma": sg, **r5})
            print("  K_%d line %d done" % (k, l0), round(time.time() - T0, 1), flush=True)

    check("2 H1: every splice of the Fano atom at a line of K_2-K_4 whose map is a torus (three of the six bijections for each chirality) gives "
          "a simple knot space whose old signs extend to the three new sides with no even face in exactly two ways, one class up to gauge",
          all(H1), {"totals": dict(tot), "H1 holds": sum(H1), "of": len(H1)})
    check("3 H2: on every grown torus the grown law is unsatisfiable and is the only unsatisfiable class; in its class the atom allows exactly "
          "the patterns of the replaced line's three points that the line itself allowed (it acts as that line), and in the other three classes "
          "it allows all eight (it is transparent)", all(H2), {"H2 holds": sum(H2), "of": len(H2)})
    ok4 = all(r.get("every walk resolves, winds and touches the atom", False) for r in H34 if "walks" not in r)
    check("4 H3: from the extended sphere state learning at the dissonance (state fixed) reaches every other class by a resolving walk, every one "
          "of which winds and changes a sign in the grown atom", ok4,
          {"configurations": len(H34), "extension a least state": sum(1 for r in H34 if r["extension violates"] == 1),
           "walks": tot["walks"]})
    by = {}
    for r in H34:
        if "cheapest walk" in r:
            by.setdefault((r["sphere"], r["distance"]), []).append(r["cheapest walk"])
    where = Counter((r["distance"] == 0, r["violated line in"]) for r in H34)
    check("5 H4 (computed): the cheapest resolving walk by sphere and placement distance (0 = grown at the dissonance), and where the "
          "extended state's violated line sits", True,
          {"cheapest walk (min, max) by sphere and distance": {"%s d=%d" % kd: (min(v), max(v)) for kd, v in sorted(by.items())},
           "(at the dissonance, violated line in)": {str(k): v for k, v in where.items()}, "rows": H34})
    ok6 = all(r[x][0] and r[x][2] for r in H5 for x in ("R0", "R3", "R7"))
    check("6 H5 (computed): random moves (R0), sight of radius 3 (R3) and the outside distance (R7) from one seeded split of each start",
          ok6, {"runs": len(H5), "resolved and replayed": {x: sum(1 for r in H5 if r[x][0] and r[x][2]) for x in ("R0", "R3", "R7")},
                "mean steps": {x: round(sum(r[x][1] for r in H5) / max(len(H5), 1), 2) for x in ("R0", "R3", "R7")}, "rows": H5})

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
        print("result.json reproduced" if not diff else "result.json differs: %s" % diff)
        sys.exit(0 if not diff else 1)


if __name__ == "__main__":
    main()
