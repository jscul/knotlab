#!/usr/bin/env python3
"""Checks for FOUR-PLACE-20261031-001C: the not-exactly-two and twelve classes build equality and are NP-complete on 4-regular systems.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Uses ticket A's library (bound by hash). Run with the repository's .venv (networkx, pysat)."""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A_DIR = ROOT / "proofs/FOUR-PLACE-20261031-001A/FOUR-PLACE-20261031-001A-P001_the_value_free_four_place_knots"
sys.path.insert(0, str(A_DIR))
import four_lib as F  # noqa: E402

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


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
a_res = json.loads((A_DIR / "result.json").read_text())
check("0 dependency artifacts bound by hash; ticket A passed", not bad and a_res["status"] == "passed",
      {"parents": len(manifest["parent_bindings"]), "mismatched": bad})
CL = F.classes()

# ------------------------------------------------------------------------------------------------ 1. the link pieces
PIECES = {}
for name in ("not-exactly-two", "twelve"):
    for lines in F.structures(5, norep=True):
        acc = F.accepted_relations(lines, 5, CL[name])
        hits = [(rel, choice, F.link_form(rel)) for rel, choice in acc.items() if F.link_form(rel)]
        # the free ports must lie on different lines, so that an absorber point never meets one line twice
        hits = [h for h in hits if not any(5 + h[2][2][0] in L and 5 + h[2][2][1] in L for L in lines)]
        hits.sort(key=lambda h: (h[2][0] != "=", sorted(h[0])))
        if hits:
            rel, choice, (kind, ab, cd) = hits[0]
            PIECES[name] = (lines, choice, kind, ab, cd, rel)
            break
info, ok1 = {}, True
for name, (lines, choice, kind, ab, cd, rel) in PIECES.items():
    # independent recomputation of the accepted relation by brute force over all 2^9 assignments
    brute = set()
    for a in range(1 << 9):
        if all(tuple(a >> p & 1 for p in L) in R for L, R in zip(lines, choice)):
            brute.add(tuple(a >> p & 1 for p in range(5, 9)))
    target = frozenset(s for s in F.H4 if (s[ab[0]] == s[ab[1]]) == (kind == "="))
    deg = [sum(p in L for L in lines) for p in range(9)]
    ok = frozenset(brute) == rel == target and deg == [4] * 5 + [1] * 4 and len(set(lines)) == len(lines) \
        and all(R in CL[name] for R in choice) and not any(5 + cd[0] in L and 5 + cd[1] in L for L in lines)
    ok1 &= ok
    info[name] = {"lines": lines, "relations (truth tables over 0000..1111, in line order)": [bits(R) for R in choice],
                  "link": f"port {5 + ab[0]} {kind} port {5 + ab[1]}", "free ports": [5 + cd[0], 5 + cd[1]], "accepted": len(rel)}
check("1 each class has a piece with five internal points (degree 4), four ports (degree 1) and six distinct lines whose accepted relation "
      "is (a rel b) x {0,1}^2 with rel equality or disequality: two ports linked, two free on different lines (recomputed by brute force)",
      set(PIECES) == {"not-exactly-two", "twelve"} and ok1, info)

# ------------------------------------------------------------------------------------------------ 2. Schaefer
sch = next(v for k, v in a_res["checks"].items() if k.startswith("3 "))
check("2 neither class is closed under a Schaefer polymorphism (ticket A, check 3), so with unbounded occurrences both are NP-complete",
      sch["pass"] and sch["info"]["not-exactly-two"] == [] and sch["info"]["twelve"] == [], sch["info"])

# ------------------------------------------------------------------------------------------------ 3. the regularization, end to end
rng = random.Random(20261031)
e2e, tallies = [], {}
for name, (lines, choice, kind, ab, cd, rel) in PIECES.items():
    piece = (lines, choice, kind, ab, cd)
    sat_n = unsat_n = 0
    for t in range(80):
        nv = rng.randint(4, 9)
        m = rng.randint(1, 3 * nv)
        cons = [(tuple(rng.sample(range(nv), 4)), rng.choice(CL[name])) for _ in range(m)]
        used = sorted({x for vs, _ in cons for x in vs})
        ren = {x: i for i, x in enumerate(used)}
        cons = [(tuple(ren[x] for x in vs), R) for vs, R in cons]
        nv = len(used)
        src = F.sat([vs for vs, _ in cons], [R for _, R in cons])
        L2, R2 = F.regularize(nv, cons, piece)
        props = {"4-regular, 4-uniform, simple": F.is_regular_system(L2), "no repeated lines": len({frozenset(L) for L in L2}) == len(L2),
                 "same satisfiability": F.sat(L2, R2) == src, "relations in the class": all(R in CL[name] for R in R2)}
        if not all(props.values()):
            e2e.append((name, t, props))
        sat_n += src
        unsat_n += not src
    tallies[name] = {"instances": 80, "satisfiable": sat_n, "unsatisfiable": unsat_n}
check("3 regularization end to end: 160 random instances (4-9 variables, up to 27 constraints) map to simple 4-regular 4-uniform systems "
      "without repeated lines, over the same class, with the same satisfiability (SAT solver on both)",
      not e2e and all(v["satisfiable"] > 5 and v["unsatisfiable"] > 5 for v in tallies.values()), {"tallies": tallies, "failures": e2e[:2]})

# ------------------------------------------------------------------------------------------------ 4. control
name = "twelve"
lines, choice, kind, ab, cd, rel = PIECES[name]
decoupled = None
for structure in F.structures(5, norep=True):
    for r, ch in F.accepted_relations(structure, 5, CL[name]).items():
        if len(r) == 16:
            decoupled = (structure, ch)
            break
    if decoupled:
        break
broken = 0
for t in range(60):
    nv = rng.randint(4, 7)
    cons = [(tuple(rng.sample(range(nv), 4)), rng.choice(CL[name])) for _ in range(rng.randint(nv, 3 * nv))]
    used = sorted({x for vs, _ in cons for x in vs})
    ren = {x: i for i, x in enumerate(used)}
    cons = [(tuple(ren[x] for x in vs), R) for vs, R in cons]
    src = F.sat([vs for vs, _ in cons], [R for _, R in cons])
    L2, R2 = F.regularize(len(used), cons, (decoupled[0], decoupled[1], "=", (0, 1), (2, 3)))
    broken += F.sat(L2, R2) != src
check("4 control: with a piece that accepts everything in place of the link, copies decouple and satisfiability changes on some instances",
      decoupled is not None and broken > 0, {"instances whose satisfiability changed (of 60)": broken})

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
