#!/usr/bin/env python3
"""Checks for UNIFORM-FANO-20261107-001A: the Fano plane is the only uniform law that contradicts itself.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (pysat, sympy). Single process; a few minutes."""
import hashlib
import itertools
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import fano_lib as FL  # noqa: E402
U, T = FL.U, FL.T

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    rng = random.Random(20261107)
    LAWS = FL.census(rng)

    rows, kinds = [], Counter()
    ok_sign, ok_brace, unsat = True, True, []
    for name, x, y in LAWS:
        G, lines = FL.cayley_lines(x, y)
        if len(G) > 720:
            kinds["larger than 720 (skipped)"] += 1
            continue
        if not FL.simple(lines):
            kinds["not simple"] += 1
            continue
        kinds["simple"] += 1
        n = len(G)
        for sigma in itertools.product((0, 1), repeat=3):
            if len(set(sigma)) > 1:
                ok_sign &= FL.constant_assignment_works(lines, sigma)
        br = FL.brace(x, y)
        ok_brace &= br
        col = FL.colourable(lines, n)
        if not col:
            unsat.append((name, n))
        rows.append((name, n, br, col))
    check("1 with non-constant uniform signs the all-zero assignment satisfies every line of every simple Cayley law", ok_sign,
          {"laws": kinds["simple"]})
    check("2 the brace lemma: every simple Cayley law in the census has a brace for its incidence graph (the Cayley digraph of {x, xy} "
          "stays strongly connected without the identity)", ok_brace,
          {"simple laws": kinds["simple"], "skipped (a line repeats a point)": kinds["not simple"],
           "group orders": sorted({r[1] for r in rows})})
    fano_only = all(n == 7 for _, n in unsat) and len(unsat) >= 1
    check("3 among them, under equal signs (a plain 2-colouring), the only unsatisfiable laws are the Fano plane (n = 7)", fano_only,
          {"unsatisfiable": unsat})

    # 4. the Fano plane: sign-nonsingular, its digraph F7 has no even dicycle, its incidence graph is a brace
    F = T.FANO
    M = next(dict(enumerate(perm)) for perm in itertools.permutations(range(7))
             if all(perm[l] in F[l] for l in range(7)))       # a perfect matching line -> point
    D = T.digraph(F, M)
    A = T.matrix(F)
    fano_ok = (not T.colourable(F)) and T.sns(F) and abs(int(T.det(A))) == int(T.permanent(A)) == 24 and not T.has_even_dicycle(D)
    fano_ok &= not T.tight_cuts(F)
    check("4 the Fano plane: not 2-colourable, sign-nonsingular (|det| = per = 24), its digraph F7 has no even dicycle, and it has no "
          "nontrivial tight cut", fano_ok, {})

    # 5. controls
    ctrl = {}
    P13 = T.point_splice(F, 0, F, F[0])
    tc = T.tight_cuts(P13, max_shore=7)
    def strongly_2_connected(Dg):
        """remove each vertex in turn; the rest must stay strongly connected"""
        V = list(Dg)
        for r in V:
            rest = [v for v in V if v != r]
            for fwd in (True, False):
                adj = {v: [] for v in rest}
                for u in rest:
                    for w in Dg[u]:
                        if w != r:
                            (adj[u] if fwd else adj[w]).append(w if fwd else u)
                seen, st = {rest[0]}, [rest[0]]
                while st:
                    u = st.pop()
                    for w in adj[u]:
                        if w not in seen:
                            seen.add(w)
                            st.append(w)
                if len(seen) < len(rest):
                    return False
        return True
    M13 = next(m for m in T.perfect_matchings(P13))
    M13 = M13 if isinstance(M13, dict) else dict(enumerate(M13))
    ctrl["the 13-point Fano splice is not 2-colourable and has a nontrivial tight cut"] = (not T.colourable(P13)) and len(tc) > 0
    ctrl["the brace test says no on the 13-point splice (its digraph is not strongly 2-connected) and yes on the Fano plane"] = (
        not strongly_2_connected(T.digraph(P13, M13))) and strongly_2_connected(D)
    G7, lines7 = FL.cayley_lines(tuple((i + 1) % 7 for i in range(7)), tuple((i + 3) % 7 for i in range(7)))
    ctrl["Z7 with lines {g, g+1, g+4} (not a difference set) is 2-colourable"] = FL.colourable(lines7, 7)
    x4 = tuple((i + 1) % 8 for i in range(8))
    G8, lines8 = FL.cayley_lines(x4, U.inv(x4))
    ctrl["a law with a repeated point fails simplicity"] = not FL.simple(lines8)
    check("5 controls: each check can fail", all(ctrl.values()), ctrl)

    out = {"status": "passed", "checks": OUT}
    res = HERE / "result.json"
    if "--write" in sys.argv:
        res.write_text(json.dumps(out, indent=1, default=str) + "\n")
        print("wrote", res)
    else:
        old = json.loads(res.read_text())
        same = json.loads(json.dumps(out, default=str))["checks"] == old["checks"]
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
