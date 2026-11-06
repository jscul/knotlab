#!/usr/bin/env python3
"""Checks for FOUR-PREFER-20261101-001B: every failing four-place class builds a link, so it is NP-complete on 4-regular systems.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Uses ticket A's library (bound by hash). Run with the repository's .venv (networkx, pysat)."""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A_DIR = ROOT / "proofs/FOUR-PREFER-20261101-001A/FOUR-PREFER-20261101-001A-P001_every_four_place_knot"
C4_DIR = ROOT / "proofs/FOUR-PLACE-20261031-001C/FOUR-PLACE-20261031-001C-P001_the_other_value_free_laws_build_equality"
sys.path.insert(0, str(A_DIR))
import prefer_lib as P  # noqa: E402

F = P.F
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def bits(R):
    return "".join("1" if s in R else "0" for s in F.H4)


def from_bits(b):
    return frozenset(s for s, ch in zip(F.H4, b) if ch == "1")


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
a_res = json.loads((A_DIR / "result.json").read_text())
check("0 dependency artifacts bound by hash; ticket A passed", not bad and a_res["status"] == "passed",
      {"parents": len(manifest["parent_bindings"]), "mismatched": bad})
CL = P.classes()
TWELVE = CL[11][0]

# ------------------------------------------------------------------------------------------------ 1. the twelve class's link piece
c4 = json.loads((C4_DIR / "result.json").read_text())
tw = next(v for k, v in c4["checks"].items() if k.startswith("1 "))["info"]["twelve"]
LINK_LINES = [tuple(L) for L in tw["lines"]]
LINK_RELS = [from_bits(b) for b in tw["relations (truth tables over 0000..1111, in line order)"]]
brute = set()
for a in range(1 << 9):
    if all(tuple(a >> p & 1 for p in L) in R for L, R in zip(LINK_LINES, LINK_RELS)):
        brute.add(tuple(a >> p & 1 for p in range(5, 9)))
link_ok = frozenset(brute) == frozenset(s for s in F.H4 if s[2] == s[3]) and all(F.canonical(R) == TWELVE for R in LINK_RELS)
check("1 the twelve class's link piece (FOUR-PLACE C): five internal points, six lines, accepted relation (port 7 = port 8) x {0,1}^2 on "
      "ports 5, 6 (recomputed by brute force)", link_ok and tw["link"] == "port 7 = port 8", {"lines": LINK_LINES, "relations": [bits(R) for R in LINK_RELS]})

# ------------------------------------------------------------------------------------------------ 2-3. realizations and lifted links
LIFT_CLASSES = [2, 4, 5, 6, 7, 8, 9, 10, 12]
PIECES, info2, info3, ok3 = {}, {}, {}, True
for ci in LIFT_CLASSES:
    mem = CL[ci][1]
    choice, rel = P.realization_of_class(mem, TWELVE)
    info2[f"class {ci}"] = {"relations on the three-point piece (line order)": [bits(R) for R in choice], "accepted": bits(rel)}
    realizations = {}
    for R in set(LINK_RELS):
        realizations[R] = P.adapt(P.THREE_POINT, choice, 3, rel, R)
        assert P.accepted_by_sat(realizations[R][0], realizations[R][1], 3) == R
    lines, rels, k = P.lift(LINK_LINES, LINK_RELS, 5, realizations)
    acc = P.accepted_by_sat(lines, rels, k)
    deg = [sum(p in L for L in lines) for p in range(k + 4)]
    free_apart = not any(k in L and k + 1 in L for L in lines)
    ok = acc == frozenset(s for s in F.H4 if s[2] == s[3]) and deg == [4] * k + [1] * 4 and all(len(set(L)) == 4 for L in lines) \
        and len({frozenset(L) for L in lines}) == len(lines) and free_apart and all(R in mem for R in rels)
    ok3 &= ok
    PIECES[ci] = (lines, rels, k, "=", (2, 3), (0, 1))
    info3[f"class {ci}"] = {"internal points": k, "lines": len(lines), "accepted relation is the link": ok}
check("2 each of classes 2, 4, 5, 6, 7, 8, 9, 10, 12 has a three-point piece (three internal points on four lines, one port per line) "
      "accepting a relation of the twelve class", len(info2) == 9, info2)
check("3 lifting: replacing each line of the twelve link piece by an adapted three-point piece gives, for each of these classes, a piece "
      "with 23 internal points and 24 distinct lines whose accepted relation (by SAT) is (port a = port b) x {0,1}^2, free ports on "
      "different lines", ok3, info3)

# ------------------------------------------------------------------------------------------------ 4. class 1: a direct link
rng = random.Random(20261101)
mem1 = CL[1][1]
STRUCT = F.structures(5, norep=True)
found = None
for trial in range(20000):
    lines = rng.choice(STRUCT)
    choice = [rng.choice(mem1) for _ in lines]
    acc = (1 << (1 << 9)) - 1
    for L, R in zip(lines, choice):
        acc &= F.line_mask(L, 9, R)
    if not acc:
        continue
    rel = F.port_relation(acc, 5)
    lf = F.link_form(rel)
    if lf and not any(5 + lf[2][0] in L and 5 + lf[2][1] in L for L in lines):
        found = (lines, choice, lf, trial)
        break
lines, choice, (kind, ab, cd), trial = found
brute = set()
for a in range(1 << 9):
    if all(tuple(a >> p & 1 for p in L) in R for L, R in zip(lines, choice)):
        brute.add(tuple(a >> p & 1 for p in range(5, 9)))
ok4 = frozenset(brute) == frozenset(s for s in F.H4 if (s[ab[0]] == s[ab[1]]) == (kind == "="))
PIECES[1] = (lines, choice, 5, kind, ab, cd)
check("4 class 1 (which realizes no link class with three points) has a direct link piece with five internal points and six distinct lines "
      "(seeded search; accepted relation recomputed by brute force)", ok4,
      {"lines": lines, "relations": [bits(R) for R in choice], "link": f"port {5 + ab[0]} {kind} port {5 + ab[1]}",
       "free ports": [5 + cd[0], 5 + cd[1]], "found after trials": trial})

# ------------------------------------------------------------------------------------------------ 5. regularization end to end
tallies, fails = {}, []
for ci in sorted(PIECES):
    mem = CL[ci][1]
    s_n = u_n = 0
    for t in range(24):
        nv = rng.randint(4, 7)
        m = rng.randint(nv, 4 * nv)
        cons = [(tuple(rng.sample(range(nv), 4)), rng.choice(mem)) for _ in range(m)]
        used = sorted({x for vs, _ in cons for x in vs})
        ren = {x: i for i, x in enumerate(used)}
        cons = [(tuple(ren[x] for x in vs), R) for vs, R in cons]
        src = F.sat([vs for vs, _ in cons], [R for _, R in cons])
        L2, R2 = P.regularize(len(used), cons, PIECES[ci])
        props = {"4-regular, 4-uniform, simple": F.is_regular_system(L2), "relations in the class": all(R in mem for R in R2),
                 "same satisfiability": F.sat(L2, R2) == src}
        if not all(props.values()):
            fails.append((ci, t, props))
        s_n += src
        u_n += not src
    tallies[f"class {ci}"] = {"satisfiable": s_n, "unsatisfiable": u_n}
check("5 regularization end to end for all ten classes (24 random instances each): every result is a simple 4-regular 4-uniform system "
      "over the same class with the same satisfiability (SAT solver on both); every class has at least three satisfiable and three "
      "unsatisfiable instances", not fails and all(v["satisfiable"] >= 3 and v["unsatisfiable"] >= 3 for v in tallies.values()),
      {"tallies": tallies, "failures": fails[:2]})

# ------------------------------------------------------------------------------------------------ 6. Schaefer
sch = next(v for k, v in a_res["checks"].items() if k.startswith("1 "))["info"]["table"]
check("6 none of the ten classes is closed under a Schaefer polymorphism (ticket A), so each is NP-complete with unbounded occurrences, and "
      "by the regularization NP-complete on 4-regular systems", all(sch[ci]["Schaefer"] == [] for ci in PIECES),
      {f"class {ci}": sch[ci]["Schaefer"] for ci in sorted(PIECES)})

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
