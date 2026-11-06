#!/usr/bin/env python3
"""Checks for FOUR-PREFER-20261101-001A: every four-place knot, and the clause never fails.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx)."""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
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


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
check("0 dependency artifacts bound by hash", not bad, {"parents": len(manifest["parent_bindings"]), "mismatched": bad})

# ------------------------------------------------------------------------------------------------ 1. the catalogue
knots = P.all_knots()
adjacent = lambda a, b: sum(x != y for x, y in zip(a, b)) == 1  # noqa: E731
indep_ok = all(not any(adjacent(a, b) for a, b in itertools.combinations([s for s in F.H4 if s not in R], 2)) for R in knots)
indep_count = sum(1 for m in range(1, 1 << 16)
                  if not any(adjacent(a, b) for a, b in itertools.combinations([s for i, s in enumerate(F.H4) if m >> i & 1], 2)))
CL = P.classes()
table = []
for i, (c, mem) in enumerate(CL):
    table.append({"class": i, "states": len(c), "relations": len(mem), "value-free": F.complement(c) == c,
                  "excluded states": 16 - len(c), "forcing places": len(P.forcing_places(c)), "Schaefer": F.schaefer_classes(mem),
                  "representative (truth table over 0000..1111)": bits(c)})
check("1 the four-place knots are the relations whose excluded states form a non-empty independent set of the 4-cube: 742 relations "
      "(743 independent sets, the empty one excluded), in 20 classes under flips and permutations",
      len(knots) == 742 and indep_ok and indep_count == 742 and len(CL) == 20 and sum(len(m) for _, m in CL) == 742,
      {"classes": len(CL), "table": table})

# ------------------------------------------------------------------------------------------------ 2. value-free classes match FOUR-PLACE A
vf = [i for i, (c, _) in enumerate(CL) if F.complement(c) == c]
four = F.classes()
check("2 four classes are value-free (0 parity, 3 not-exactly-two, 11 twelve, 18 not-all-equal), matching FOUR-PLACE A; 16 prefer a value",
      vf == [0, 3, 11, 18] and [len(CL[i][1]) for i in vf] == [len(four[k]) for k in ("parity", "not-exactly-two", "twelve", "not-all-equal")]
      and all(F.canonical(CL[i][0]) == F.canonical(four[k][0]) for i, k in zip(vf, ("parity", "not-exactly-two", "twelve", "not-all-equal"))),
      {"value-free classes": vf})

# ------------------------------------------------------------------------------------------------ 3. Schaefer and forcing places
sch = {i: t["Schaefer"] for i, t in enumerate(table)}
forcing = {i: t["forcing places"] for i, t in enumerate(table)}
check("3 only parity (class 0) is Schaefer-tractable (affine); only the clause (class 19, one excluded state) has a forcing value at every "
      "place", all((v == ["affine (minority)"]) == (i == 0) and (v == [] or i == 0) for i, v in sch.items())
      and [i for i, f in forcing.items() if f == 4] == [19], {"forcing places per class": forcing})

# ------------------------------------------------------------------------------------------------ 4. the clause never fails
rng = random.Random(20261101)
clause = CL[19][1]


def rand_regular(n):
    while True:
        stubs = [p for p in range(n) for _ in range(4)]
        rng.shuffle(stubs)
        L = [tuple(stubs[4 * i:4 * i + 4]) for i in range(n)]
        if all(len(set(l)) == 4 for l in L):
            return L


ok_random = 0
for t in range(200):
    L = rand_regular(rng.randint(5, 40))
    rels = [rng.choice(clause) for _ in L]
    ok_random += P.satisfies(L, rels, P.matching_solution(L, rels))
census = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
small = {}
for n in (4, 5):
    for i, L in enumerate(F.systems(n, census)):
        f, tot = F.failing_count(L, clause)
        small[f"n={n} #{i}"] = f"{f}/{tot}"
check("4 the clause never fails on 4-regular systems: the matching construction (Hall, then a forcing value at each line's matched point) "
      "solves 200 random signed systems with 5-40 points, and every signing of the systems with n <= 5 is solvable",
      ok_random == 200 and all(v.startswith("0/") for v in small.values()), {"random systems solved": ok_random, "small systems": small})

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
